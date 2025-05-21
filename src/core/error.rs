// HiveDB Error Module
//
// This module defines the error types used throughout the HiveDB system.

use thiserror::Error;

/// Errors that can occur in the HiveDB system
#[derive(Error, Debug)]
pub enum HiveError {
    /// A cell already exists at the specified coordinates
    #[error("A cell already exists at the specified coordinates")]
    CellAlreadyExists,
    
    /// The specified cell was not found
    #[error("Cell not found")]
    CellNotFound,
    
    /// The specified hive was not found
    #[error("Hive not found")]
    HiveNotFound,
    
    /// The specified coordinates are out of bounds
    #[error("Coordinates are out of bounds")]
    OutOfBoundsError,
    
    /// Error acquiring a lock
    #[error("Failed to acquire lock")]
    LockError,
    
    /// Error with Arc reference counting
    #[error("Reference counting error")]
    ReferenceError,
    
    /// Error getting system time
    #[error("System time error")]
    SystemTimeError,
    
    /// Error compressing data
    #[error("Compression error: {0}")]
    CompressionError(String),
    
    /// Error decompressing data
    #[error("Decompression error: {0}")]
    DecompressionError(String),
    
    /// I/O error
    #[error("I/O error: {0}")]
    IoError(String),
    
    /// Serialization error
    #[error("Serialization error: {0}")]
    SerializationError(String),
    
    /// Deserialization error
    #[error("Deserialization error: {0}")]
    DeserializationError(String),
    
    /// Authentication error
    #[error("Authentication error: {0}")]
    AuthenticationError(String),
    
    /// Authorization error
    #[error("Authorization error: {0}")]
    AuthorizationError(String),
    
    /// Schema validation error
    #[error("Schema validation error: {0}")]
    SchemaValidationError(String),
    
    /// Query error
    #[error("Query error: {0}")]
    QueryError(String),
    
    /// Network error
    #[error("Network error: {0}")]
    NetworkError(String),
    
    /// Feature not implemented
    #[error("Feature not implemented")]
    NotImplemented,
    
    /// Generic error
    #[error("Error: {0}")]
    GenericError(String),
}
