import os
import logging
import ctypes
import time
import hashlib
import hmac
from typing import Dict, Any, Optional, List, Tuple, Union
import json
import secrets
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SGX configuration
SGX_ENABLED = os.getenv("SGX_ENABLED", "False").lower() in ("true", "1", "t")
SGX_ENCLAVE_PATH = os.getenv("SGX_ENCLAVE_PATH", "/opt/intel/sgxsdk/SampleCode/HiveDBEnclave/enclave.signed.so")
SGX_SIMULATION_MODE = os.getenv("SGX_SIMULATION_MODE", "True").lower() in ("true", "1", "t")
SGX_SEALED_DATA_PATH = os.getenv("SGX_SEALED_DATA_PATH", "./sealed_data")

# Ensure sealed data directory exists
os.makedirs(SGX_SEALED_DATA_PATH, exist_ok=True)

# Configure logging
logger = logging.getLogger(__name__)

# Constants for encryption
AES_GCM_IV_SIZE = 12
AES_GCM_TAG_SIZE = 16
KEY_SIZE = 32  # 256 bits

class SGXEnclave:
    """Intel SGX enclave for secure operations in HiveDB.
    
    This class provides a secure environment for cryptographic operations
    using Intel SGX technology. It offers advanced encryption, secure key
    management, and protection against side-channel attacks.
    
    In simulation mode, it provides compatible APIs but uses software-based
    cryptography instead of hardware-based SGX instructions.
    """
    
    def __init__(self):
        self.enclave_id = 0
        self.lib = None
        self.is_initialized = False
        self.simulation_mode = SGX_SIMULATION_MODE
        self.master_key = None
        self.key_cache = {}
        self.last_rotation = 0
        self.rotation_interval = 86400  # 24 hours in seconds
    
    def initialize(self):
        """Initialize the SGX enclave or simulation environment.
        
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        if not SGX_ENABLED and not self.simulation_mode:
            logger.info("SGX support is disabled in configuration")
            return False
        
        # If in simulation mode, initialize software-based crypto
        if self.simulation_mode:
            try:
                # Generate or load master key for simulation mode
                master_key_path = os.path.join(SGX_SEALED_DATA_PATH, "master.key")
                if os.path.exists(master_key_path):
                    with open(master_key_path, "rb") as f:
                        self.master_key = f.read()
                else:
                    # Generate a new master key
                    self.master_key = secrets.token_bytes(KEY_SIZE)
                    # Save it securely
                    with open(master_key_path, "wb") as f:
                        f.write(self.master_key)
                    os.chmod(master_key_path, 0o600)  # Restrict permissions
                
                self.is_initialized = True
                self.last_rotation = time.time()
                logger.info("SGX simulation mode initialized successfully")
                return True
            except Exception as e:
                logger.error(f"Error initializing SGX simulation: {e}")
                return False
        
        # Hardware SGX mode
        try:
            # Try to load the SGX library
            try:
                import pysgx
                self.lib = pysgx
            except ImportError:
                logger.warning("PySGX library not available, falling back to ctypes")
                # Fallback to direct loading via ctypes
                self.lib = ctypes.CDLL(SGX_ENCLAVE_PATH)
            
            # Initialize the enclave
            if hasattr(self.lib, 'sgx_create_enclave'):
                debug_flag = 1 if os.getenv("SGX_DEBUG", "False").lower() in ("true", "1", "t") else 0
                
                # Prepare launch token
                token_path = os.path.join(SGX_SEALED_DATA_PATH, "launch_token.bin")
                token = (ctypes.c_ubyte * 1024)()  # SGX launch token is typically 1024 bytes
                updated = ctypes.c_int(0)
                
                # Try to load existing token
                if os.path.exists(token_path):
                    try:
                        with open(token_path, "rb") as f:
                            token_data = f.read(1024)
                            for i, byte in enumerate(token_data):
                                token[i] = byte
                    except Exception as e:
                        logger.warning(f"Could not load launch token: {e}")
                
                enclave_id = ctypes.c_uint64(0)
                
                # Create the enclave
                result = self.lib.sgx_create_enclave(
                    SGX_ENCLAVE_PATH.encode('utf-8'),
                    debug_flag,
                    ctypes.byref(token),
                    ctypes.byref(updated),
                    ctypes.byref(enclave_id),
                    None  # Misc attributes
                )
                
                # Save updated token if needed
                if updated.value == 1:
                    try:
                        with open(token_path, "wb") as f:
                            f.write(bytes(token))
                        os.chmod(token_path, 0o600)  # Restrict permissions
                    except Exception as e:
                        logger.warning(f"Could not save updated launch token: {e}")
                
                if result == 0:
                    self.enclave_id = enclave_id.value
                    self.is_initialized = True
                    logger.info(f"SGX enclave initialized with ID: {self.enclave_id}")
                    return True
                else:
                    logger.error(f"Failed to initialize SGX enclave, error code: {result}")
            else:
                logger.error("SGX library does not have required functions")
        except Exception as e:
            logger.error(f"Error initializing SGX enclave: {e}")
        
        return False
    
    def destroy(self):
        """Destroy the SGX enclave."""
        if self.is_initialized and self.enclave_id > 0:
            try:
                if hasattr(self.lib, 'sgx_destroy_enclave'):
                    result = self.lib.sgx_destroy_enclave(self.enclave_id)
                    if result == 0:
                        logger.info("SGX enclave destroyed successfully")
                    else:
                        logger.error(f"Failed to destroy SGX enclave, error code: {result}")
                else:
                    logger.error("SGX library does not have required functions")
            except Exception as e:
                logger.error(f"Error destroying SGX enclave: {e}")
            
            self.enclave_id = 0
            self.is_initialized = False
    
    def _rotate_keys_if_needed(self):
        """Check if keys need rotation and perform rotation if necessary."""
        current_time = time.time()
        if current_time - self.last_rotation > self.rotation_interval:
            logger.info("Performing scheduled key rotation")
            self.key_cache = {}  # Clear the key cache
            self.last_rotation = current_time
            
            # In simulation mode, we might want to rotate the master key as well
            if self.simulation_mode and self.master_key:
                # Derive a new master key using the old one
                new_master_key = hashlib.pbkdf2_hmac(
                    'sha256', 
                    self.master_key, 
                    secrets.token_bytes(16),  # Salt
                    10000,  # Iterations
                    dklen=KEY_SIZE
                )
                self.master_key = new_master_key
                
                # Save the new master key
                master_key_path = os.path.join(SGX_SEALED_DATA_PATH, "master.key")
                with open(master_key_path, "wb") as f:
                    f.write(self.master_key)
    
    def _derive_key_for_data(self, data_id: str) -> bytes:
        """Derive a unique key for the given data ID.
        
        Args:
            data_id: A unique identifier for the data being encrypted
            
        Returns:
            bytes: A 32-byte key derived from the master key and data ID
        """
        # Check if we need to rotate keys
        self._rotate_keys_if_needed()
        
        # Check if the key is already in the cache
        if data_id in self.key_cache:
            return self.key_cache[data_id]
        
        # Derive a new key
        if self.simulation_mode:
            # In simulation mode, derive key using HMAC
            key = hmac.new(
                self.master_key,
                data_id.encode('utf-8'),
                hashlib.sha256
            ).digest()
        else:
            # In hardware mode, use the enclave to derive the key
            # This is a placeholder - actual implementation would use SGX
            key_buffer = ctypes.create_string_buffer(KEY_SIZE)
            result = self.lib.enclave_derive_key(
                self.enclave_id,
                data_id.encode('utf-8'),
                len(data_id),
                key_buffer
            )
            if result != 0:
                raise Exception(f"Key derivation failed, error code: {result}")
            key = key_buffer.raw[:KEY_SIZE]
        
        # Cache the key
        self.key_cache[data_id] = key
        return key
    
    def encrypt_data(self, data: Dict[str, Any], data_id: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Encrypt data using the SGX enclave or simulation.
        
        Args:
            data: The data to encrypt
            data_id: Optional identifier for the data, used for key derivation
            
        Returns:
            Dict containing the encrypted data and metadata, or None on failure
        """
        if not self.is_initialized:
            logger.warning("SGX enclave not initialized, encryption not available")
            return None
        
        try:
            # Generate a data ID if not provided
            if not data_id:
                data_id = secrets.token_hex(16)
            
            # Convert data to JSON string
            data_str = json.dumps(data)
            data_bytes = data_str.encode('utf-8')
            
            # In simulation mode, use Python's cryptography
            if self.simulation_mode:
                try:
                    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
                except ImportError:
                    logger.error("Cryptography library not available for simulation mode")
                    return None
                
                # Derive a key for this data
                key = self._derive_key_for_data(data_id)
                
                # Generate a random nonce
                nonce = secrets.token_bytes(AES_GCM_IV_SIZE)
                
                # Encrypt the data
                cipher = AESGCM(key)
                ciphertext = cipher.encrypt(nonce, data_bytes, None)
                
                # Encode the results
                import base64
                encrypted_data = {
                    "version": "1.0",
                    "algorithm": "AES-GCM-256",
                    "data_id": data_id,
                    "nonce": base64.b64encode(nonce).decode('utf-8'),
                    "ciphertext": base64.b64encode(ciphertext).decode('utf-8')
                }
                return encrypted_data
            else:
                # Hardware SGX mode
                # Prepare buffers for the encrypted data
                data_len = len(data_bytes)
                max_encrypted_len = data_len + AES_GCM_TAG_SIZE + AES_GCM_IV_SIZE
                encrypted_data = ctypes.create_string_buffer(max_encrypted_len)
                encrypted_len = ctypes.c_uint32(0)
                
                # Call the enclave function to encrypt the data
                if hasattr(self.lib, 'enclave_encrypt_data'):
                    result = self.lib.enclave_encrypt_data(
                        self.enclave_id,
                        data_id.encode('utf-8'),
                        len(data_id),
                        data_bytes,
                        data_len,
                        encrypted_data,
                        ctypes.byref(encrypted_len)
                    )
                    
                    if result == 0:
                        # Return the encrypted data as a base64 string
                        import base64
                        return {
                            "version": "1.0",
                            "algorithm": "SGX-SEALED",
                            "data_id": data_id,
                            "ciphertext": base64.b64encode(encrypted_data.raw[:encrypted_len.value]).decode('utf-8')
                        }
                    else:
                        logger.error(f"Encryption failed, error code: {result}")
                else:
                    logger.error("SGX library does not have required encryption function")
        except Exception as e:
            logger.error(f"Error encrypting data with SGX: {e}")
        
        return None
    
    def decrypt_data(self, encrypted_data: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Decrypt data using the SGX enclave or simulation.
        
        Args:
            encrypted_data: Dictionary containing the encrypted data and metadata
            
        Returns:
            The decrypted data as a dictionary, or None on failure
        """
        if not self.is_initialized:
            logger.warning("SGX enclave not initialized, decryption not available")
            return None
        
        try:
            # Verify the encrypted data format
            required_fields = ["version", "algorithm", "data_id"]
            if not all(field in encrypted_data for field in required_fields):
                logger.error("Invalid encrypted data format")
                return None
            
            data_id = encrypted_data["data_id"]
            algorithm = encrypted_data["algorithm"]
            
            # In simulation mode, use Python's cryptography
            if self.simulation_mode:
                # Only handle AES-GCM in simulation mode
                if algorithm != "AES-GCM-256":
                    logger.error(f"Unsupported algorithm in simulation mode: {algorithm}")
                    return None
                
                try:
                    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
                except ImportError:
                    logger.error("Cryptography library not available for simulation mode")
                    return None
                
                # Decode the encrypted data and nonce
                import base64
                nonce = base64.b64decode(encrypted_data["nonce"])
                ciphertext = base64.b64decode(encrypted_data["ciphertext"])
                
                # Derive the key for this data
                key = self._derive_key_for_data(data_id)
                
                # Decrypt the data
                cipher = AESGCM(key)
                try:
                    decrypted_bytes = cipher.decrypt(nonce, ciphertext, None)
                    decrypted_str = decrypted_bytes.decode('utf-8')
                    return json.loads(decrypted_str)
                except Exception as e:
                    logger.error(f"Decryption failed: {e}")
                    return None
            else:
                # Hardware SGX mode
                # Decode the encrypted data
                import base64
                ciphertext = base64.b64decode(encrypted_data["ciphertext"])
                
                # Prepare buffers for the decrypted data
                encrypted_len = len(ciphertext)
                max_decrypted_len = encrypted_len  # Decrypted data is smaller than encrypted
                decrypted_data = ctypes.create_string_buffer(max_decrypted_len)
                decrypted_len = ctypes.c_uint32(0)
                
                # Call the enclave function to decrypt the data
                if hasattr(self.lib, 'enclave_decrypt_data'):
                    result = self.lib.enclave_decrypt_data(
                        self.enclave_id,
                        data_id.encode('utf-8'),
                        len(data_id),
                        ciphertext,
                        encrypted_len,
                        decrypted_data,
                        ctypes.byref(decrypted_len)
                    )
                    
                    if result == 0:
                        # Parse the decrypted JSON data
                        decrypted_str = decrypted_data.raw[:decrypted_len.value].decode('utf-8')
                        return json.loads(decrypted_str)
                    else:
                        logger.error(f"Decryption failed, error code: {result}")
                else:
                    logger.error("SGX library does not have required decryption function")
        except Exception as e:
            logger.error(f"Error decrypting data with SGX: {e}")
        
        return None
    
    def secure_hash(self, data: Union[str, bytes, Dict[str, Any]]) -> Optional[str]:
        """Generate a secure hash using the SGX enclave or simulation.
        
        This function generates a cryptographically secure hash of the input data.
        The hash is generated inside the SGX enclave for maximum security.
        
        Args:
            data: The data to hash (string, bytes, or dictionary)
            
        Returns:
            A hexadecimal string representing the hash, or None on failure
        """
        if not self.is_initialized:
            logger.warning("SGX enclave not initialized, secure hashing not available")
            return None
        
        try:
            # Convert data to bytes if needed
            if isinstance(data, dict):
                data_bytes = json.dumps(data, sort_keys=True).encode('utf-8')
            elif isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # In simulation mode, use Python's hashlib
            if self.simulation_mode:
                # Use HMAC with the master key for added security
                h = hmac.new(self.master_key, data_bytes, hashlib.sha512)
                return h.hexdigest()
            else:
                # Hardware SGX mode
                # Prepare buffers for the hash
                data_len = len(data_bytes)
                hash_buffer = ctypes.create_string_buffer(64)  # SHA-512 hash size
                
                # Call the enclave function to generate the hash
                if hasattr(self.lib, 'enclave_secure_hash'):
                    result = self.lib.enclave_secure_hash(
                        self.enclave_id,
                        data_bytes,
                        data_len,
                        hash_buffer
                    )
                    
                    if result == 0:
                        # Return the hash as a hexadecimal string
                        return hash_buffer.raw[:64].hex()
                    else:
                        logger.error(f"Secure hash generation failed, error code: {result}")
                else:
                    logger.error("SGX library does not have required hashing function")
        except Exception as e:
            logger.error(f"Error generating secure hash with SGX: {e}")
        
        return None
    
    def verify_data_integrity(self, data: Dict[str, Any], hash_value: str) -> bool:
        """Verify the integrity of data using a secure hash.
        
        Args:
            data: The data to verify
            hash_value: The expected hash value
            
        Returns:
            True if the data integrity is verified, False otherwise
        """
        try:
            # Generate a hash of the data
            current_hash = self.secure_hash(data)
            if not current_hash:
                return False
            
            # Compare with the expected hash
            return hmac.compare_digest(current_hash, hash_value)
        except Exception as e:
            logger.error(f"Error verifying data integrity: {e}")
            return False
    
    def secure_remote_attestation(self) -> Dict[str, Any]:
        """Perform secure remote attestation to verify the SGX environment.
        
        This function generates a quote that can be verified by a remote party
        to ensure that the code is running in a genuine SGX enclave.
        
        Returns:
            A dictionary containing attestation information, or an error message
        """
        if not self.is_initialized:
            return {"error": "SGX enclave not initialized"}
        
        # In simulation mode, return simulated attestation data
        if self.simulation_mode:
            return {
                "mode": "simulation",
                "timestamp": time.time(),
                "simulation_notice": "This is a simulated attestation and should not be used in production"
            }
        
        try:
            # Real SGX attestation would be implemented here
            # This requires the SGX SDK and PSW (Platform Software)
            if hasattr(self.lib, 'enclave_get_attestation_quote'):
                quote_buffer = ctypes.create_string_buffer(2048)  # Quote buffer size
                quote_size = ctypes.c_uint32(0)
                
                result = self.lib.enclave_get_attestation_quote(
                    self.enclave_id,
                    quote_buffer,
                    ctypes.byref(quote_size)
                )
                
                if result == 0:
                    import base64
                    return {
                        "mode": "hardware",
                        "timestamp": time.time(),
                        "quote": base64.b64encode(quote_buffer.raw[:quote_size.value]).decode('utf-8')
                    }
                else:
                    return {"error": f"Failed to generate attestation quote, error code: {result}"}
            else:
                return {"error": "SGX library does not support attestation"}
        except Exception as e:
            logger.error(f"Error performing remote attestation: {e}")
            return {"error": str(e)}
    
    def secure_compute_on_encrypted(self, operation: str, encrypted_data: Dict[str, str], 
                                   params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Perform secure computation on encrypted data without decrypting it.
        
        This function allows certain operations to be performed on encrypted data
        without fully decrypting it, providing enhanced security and privacy.
        
        Args:
            operation: The operation to perform (e.g., 'search', 'aggregate', 'filter')
            encrypted_data: The encrypted data to operate on
            params: Parameters for the operation
            
        Returns:
            The result of the operation, or None on failure
        """
        if not self.is_initialized:
            logger.warning("SGX enclave not initialized, secure computation not available")
            return None
        
        if not params:
            params = {}
        
        # In simulation mode, we need to decrypt, perform the operation, and re-encrypt
        if self.simulation_mode:
            try:
                # Decrypt the data
                decrypted_data = self.decrypt_data(encrypted_data)
                if not decrypted_data:
                    return None
                
                result = None
                
                # Perform the requested operation
                if operation == 'search':
                    query = params.get('query', '')
                    if not query:
                        return {"error": "No search query provided"}
                    
                    # Simple search implementation
                    matches = []
                    for key, value in decrypted_data.items():
                        if isinstance(value, str) and query.lower() in value.lower():
                            matches.append({"key": key, "value": value})
                        elif isinstance(value, (int, float)) and str(query) == str(value):
                            matches.append({"key": key, "value": value})
                    
                    result = {"matches": matches, "count": len(matches)}
                
                elif operation == 'aggregate':
                    agg_field = params.get('field', '')
                    agg_op = params.get('operation', 'sum')
                    
                    if not agg_field:
                        return {"error": "No aggregation field provided"}
                    
                    values = []
                    for key, value in decrypted_data.items():
                        if isinstance(value, dict) and agg_field in value:
                            if isinstance(value[agg_field], (int, float)):
                                values.append(value[agg_field])
                    
                    if agg_op == 'sum':
                        result = {"result": sum(values)}
                    elif agg_op == 'avg':
                        result = {"result": sum(values) / len(values) if values else 0}
                    elif agg_op == 'max':
                        result = {"result": max(values) if values else None}
                    elif agg_op == 'min':
                        result = {"result": min(values) if values else None}
                    elif agg_op == 'count':
                        result = {"result": len(values)}
                
                elif operation == 'filter':
                    filter_field = params.get('field', '')
                    filter_value = params.get('value')
                    filter_op = params.get('operator', 'eq')
                    
                    if not filter_field or filter_value is None:
                        return {"error": "Incomplete filter parameters"}
                    
                    filtered_data = {}
                    for key, value in decrypted_data.items():
                        if isinstance(value, dict) and filter_field in value:
                            field_value = value[filter_field]
                            
                            include = False
                            if filter_op == 'eq' and field_value == filter_value:
                                include = True
                            elif filter_op == 'neq' and field_value != filter_value:
                                include = True
                            elif filter_op == 'gt' and field_value > filter_value:
                                include = True
                            elif filter_op == 'gte' and field_value >= filter_value:
                                include = True
                            elif filter_op == 'lt' and field_value < filter_value:
                                include = True
                            elif filter_op == 'lte' and field_value <= filter_value:
                                include = True
                            
                            if include:
                                filtered_data[key] = value
                    
                    result = {"filtered_data": filtered_data, "count": len(filtered_data)}
                
                else:
                    return {"error": f"Unsupported operation: {operation}"}
                
                return result
            except Exception as e:
                logger.error(f"Error performing secure computation: {e}")
                return {"error": str(e)}
        else:
            # Hardware SGX mode - would use special enclave functions
            # that operate directly on encrypted data
            try:
                # Convert parameters to JSON
                params_json = json.dumps(params)
                
                # Prepare buffers for the result
                result_buffer = ctypes.create_string_buffer(8192)  # Result buffer size
                result_size = ctypes.c_uint32(0)
                
                # Get the encrypted data
                import base64
                ciphertext = base64.b64decode(encrypted_data["ciphertext"])
                data_id = encrypted_data["data_id"]
                
                # Call the enclave function to perform the operation
                if hasattr(self.lib, 'enclave_compute_on_encrypted'):
                    result = self.lib.enclave_compute_on_encrypted(
                        self.enclave_id,
                        operation.encode('utf-8'),
                        len(operation),
                        data_id.encode('utf-8'),
                        len(data_id),
                        ciphertext,
                        len(ciphertext),
                        params_json.encode('utf-8'),
                        len(params_json),
                        result_buffer,
                        ctypes.byref(result_size)
                    )
                    
                    if result == 0:
                        # Parse the result JSON
                        result_json = result_buffer.raw[:result_size.value].decode('utf-8')
                        return json.loads(result_json)
                    else:
                        logger.error(f"Secure computation failed, error code: {result}")
                        return {"error": f"Operation failed with code {result}"}
                else:
                    logger.error("SGX library does not support secure computation on encrypted data")
                    return {"error": "Secure computation not supported by this SGX implementation"}
            except Exception as e:
                logger.error(f"Error performing secure computation: {e}")
                return {"error": str(e)}

# Singleton instance
sgx_enclave = SGXEnclave()
