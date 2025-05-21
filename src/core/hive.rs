// HiveDB Hive Module
//
// This module defines the Hive structure, which is the main container
// for data in the HiveDB system, similar to a database in traditional systems.

use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::{Arc, RwLock};
use serde::{Deserialize, Serialize};
use crate::core::cell::{Cell, CellDataType, CellGrid};
use crate::core::error::HiveError;
use crate::core::schema::Schema;
use log::{debug, info, warn};
use rand::Rng;

/// Initialize the hive subsystem
pub fn init() -> Result<(), HiveError> {
    info!("Initializing hive management subsystem");
    // Initialize any global hive-related resources here
    Ok(())
}

/// Represents a Hive, which is the main container for data in HiveDB
/// Similar to a database in traditional database systems
#[derive(Debug)]
pub struct Hive {
    /// Unique identifier for this hive
    pub id: String,
    
    /// Human-readable name for this hive
    pub name: String,
    
    /// Description of this hive
    pub description: String,
    
    /// When this hive was created
    pub created_at: u64,
    
    /// When this hive was last modified
    pub modified_at: u64,
    
    /// The schema for this hive
    pub schema: Option<Schema>,
    
    /// The grid of cells that make up this hive
    pub cells: CellGrid,
    
    /// Path to the storage location for this hive
    pub storage_path: PathBuf,
    
    /// Additional metadata for this hive
    pub metadata: HiveMetadata,
}

/// Metadata for a Hive
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HiveMetadata {
    /// Owner of this hive
    pub owner: String,
    
    /// Version of this hive
    pub version: u64,
    
    /// Tags associated with this hive
    pub tags: Vec<String>,
    
    /// Custom properties
    pub properties: HashMap<String, String>,
}

impl Hive {
    /// Create a new hive with the given name
    pub fn new(
        name: String,
        description: String,
        owner: String,
        storage_path: PathBuf,
        dimensions: (usize, usize),
    ) -> Result<Self, HiveError> {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map_err(|_| HiveError::SystemTimeError)?
            .as_secs();
        
        // Generate a unique ID for this hive
        let id = generate_hive_id();
        
        Ok(Self {
            id,
            name,
            description,
            created_at: now,
            modified_at: now,
            schema: None,
            cells: CellGrid::new(dimensions),
            storage_path,
            metadata: HiveMetadata {
                owner,
                version: 1,
                tags: Vec::new(),
                properties: HashMap::new(),
            },
        })
    }
    
    /// Add a cell to this hive
    pub fn add_cell(&mut self, cell: Cell) -> Result<(), HiveError> {
        self.cells.add_cell(cell)?;
        self.metadata.version += 1;
        self.update_modified_time()?;
        Ok(())
    }
    
    /// Get a cell from this hive
    pub fn get_cell(&self, coordinates: (i32, i32)) -> Option<Arc<RwLock<Cell>>> {
        self.cells.get_cell(coordinates)
    }
    
    /// Remove a cell from this hive
    pub fn remove_cell(&mut self, coordinates: (i32, i32)) -> Result<Cell, HiveError> {
        let cell = self.cells.remove_cell(coordinates)?;
        self.metadata.version += 1;
        self.update_modified_time()?;
        Ok(cell)
    }
    
    /// Set the schema for this hive
    pub fn set_schema(&mut self, schema: Schema) -> Result<(), HiveError> {
        self.schema = Some(schema);
        self.metadata.version += 1;
        self.update_modified_time()?;
        Ok(())
    }
    
    /// Add a tag to this hive
    pub fn add_tag(&mut self, tag: String) -> Result<(), HiveError> {
        if !self.metadata.tags.contains(&tag) {
            self.metadata.tags.push(tag);
            self.metadata.version += 1;
            self.update_modified_time()?;
        }
        Ok(())
    }
    
    /// Remove a tag from this hive
    pub fn remove_tag(&mut self, tag: &str) -> Result<(), HiveError> {
        let initial_len = self.metadata.tags.len();
        self.metadata.tags.retain(|t| t != tag);
        
        if self.metadata.tags.len() != initial_len {
            self.metadata.version += 1;
            self.update_modified_time()?;
        }
        
        Ok(())
    }
    
    /// Set a custom property for this hive
    pub fn set_property(&mut self, key: String, value: String) -> Result<(), HiveError> {
        self.metadata.properties.insert(key, value);
        self.metadata.version += 1;
        self.update_modified_time()?;
        Ok(())
    }
    
    /// Get a custom property from this hive
    pub fn get_property(&self, key: &str) -> Option<&String> {
        self.metadata.properties.get(key)
    }
    
    /// Remove a custom property from this hive
    pub fn remove_property(&mut self, key: &str) -> Result<(), HiveError> {
        if self.metadata.properties.remove(key).is_some() {
            self.metadata.version += 1;
            self.update_modified_time()?;
        }
        Ok(())
    }
    
    /// Get the number of cells in this hive
    pub fn cell_count(&self) -> usize {
        self.cells.cell_count()
    }
    
    /// Find cells by tag
    pub fn find_cells_by_tag(&self, tag: &str) -> Vec<Arc<RwLock<Cell>>> {
        self.cells.find_by_tag(tag)
    }
    
    /// Update the modified time for this hive
    fn update_modified_time(&mut self) -> Result<(), HiveError> {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map_err(|_| HiveError::SystemTimeError)?
            .as_secs();
        
        self.modified_at = now;
        Ok(())
    }
    
    /// Save this hive to storage
    pub fn save(&self) -> Result<(), HiveError> {
        // TODO: Implement actual storage logic
        info!("Saving hive '{}' to {}", self.name, self.storage_path.display());
        Ok(())
    }
    
    /// Load a hive from storage
    pub fn load(path: PathBuf) -> Result<Self, HiveError> {
        // TODO: Implement actual loading logic
        info!("Loading hive from {}", path.display());
        Err(HiveError::NotImplemented)
    }
}

/// HiveManager manages multiple hives
pub struct HiveManager {
    /// Map of hive IDs to hives
    hives: HashMap<String, Arc<RwLock<Hive>>>,
    
    /// Base storage path for all hives
    base_path: PathBuf,
}

impl HiveManager {
    /// Create a new hive manager
    pub fn new(base_path: PathBuf) -> Self {
        Self {
            hives: HashMap::new(),
            base_path,
        }
    }
    
    /// Create a new hive
    pub fn create_hive(
        &mut self,
        name: String,
        description: String,
        owner: String,
        dimensions: (usize, usize),
    ) -> Result<String, HiveError> {
        // Create a storage path for this hive
        let hive_path = self.base_path.join(sanitize_name(&name));
        
        // Create the hive
        let hive = Hive::new(
            name,
            description,
            owner,
            hive_path.clone(),
            dimensions,
        )?;
        
        let hive_id = hive.id.clone();
        
        // Add the hive to our map
        self.hives.insert(hive_id.clone(), Arc::new(RwLock::new(hive)));
        
        // Create the storage directory if it doesn't exist
        if !hive_path.exists() {
            std::fs::create_dir_all(&hive_path)
                .map_err(|e| HiveError::IoError(e.to_string()))?;
        }
        
        info!("Created new hive '{}' with ID {}", name, hive_id);
        
        Ok(hive_id)
    }
    
    /// Get a hive by ID
    pub fn get_hive(&self, id: &str) -> Option<Arc<RwLock<Hive>>> {
        self.hives.get(id).cloned()
    }
    
    /// Get a hive by name
    pub fn get_hive_by_name(&self, name: &str) -> Option<Arc<RwLock<Hive>>> {
        self.hives.values()
            .find(|hive_arc| {
                if let Ok(hive) = hive_arc.read() {
                    hive.name == name
                } else {
                    false
                }
            })
            .cloned()
    }
    
    /// Delete a hive
    pub fn delete_hive(&mut self, id: &str) -> Result<(), HiveError> {
        // Get the hive
        let hive_arc = self.hives.remove(id)
            .ok_or(HiveError::HiveNotFound)?;
        
        // Get exclusive access to the hive
        let hive = match Arc::try_unwrap(hive_arc) {
            Ok(lock) => lock.into_inner().map_err(|_| HiveError::LockError)?,
            Err(_) => return Err(HiveError::ReferenceError),
        };
        
        // Delete the storage directory
        if hive.storage_path.exists() {
            std::fs::remove_dir_all(&hive.storage_path)
                .map_err(|e| HiveError::IoError(e.to_string()))?;
        }
        
        info!("Deleted hive '{}' with ID {}", hive.name, id);
        
        Ok(())
    }
    
    /// List all hives
    pub fn list_hives(&self) -> Vec<(String, String)> {
        self.hives.iter()
            .filter_map(|(id, hive_arc)| {
                if let Ok(hive) = hive_arc.read() {
                    Some((id.clone(), hive.name.clone()))
                } else {
                    None
                }
            })
            .collect()
    }
    
    /// Save all hives
    pub fn save_all(&self) -> Result<(), HiveError> {
        for (id, hive_arc) in &self.hives {
            if let Ok(hive) = hive_arc.read() {
                hive.save()?;
            } else {
                warn!("Could not acquire read lock for hive {}", id);
            }
        }
        
        Ok(())
    }
    
    /// Load all hives from the base path
    pub fn load_all(&mut self) -> Result<(), HiveError> {
        // TODO: Implement actual loading logic
        info!("Loading all hives from {}", self.base_path.display());
        Ok(())
    }
}

/// Generate a unique ID for a hive
fn generate_hive_id() -> String {
    let mut rng = rand::thread_rng();
    let random_bytes: Vec<u8> = (0..16).map(|_| rng.gen::<u8>()).collect();
    
    format!("hive-{}", hex::encode(random_bytes))
}

/// Sanitize a name for use in a file path
fn sanitize_name(name: &str) -> String {
    name.chars()
        .map(|c| if c.is_alphanumeric() || c == '-' || c == '_' { c } else { '_' })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;
    
    #[test]
    fn test_hive_creation() {
        let temp_dir = tempdir().unwrap();
        let hive = Hive::new(
            "test-hive".to_string(),
            "A test hive".to_string(),
            "test-user".to_string(),
            temp_dir.path().to_path_buf(),
            (64, 64),
        ).unwrap();
        
        assert_eq!(hive.name, "test-hive");
        assert_eq!(hive.description, "A test hive");
        assert_eq!(hive.metadata.owner, "test-user");
        assert_eq!(hive.metadata.version, 1);
        assert_eq!(hive.cell_count(), 0);
    }
    
    #[test]
    fn test_hive_metadata() {
        let temp_dir = tempdir().unwrap();
        let mut hive = Hive::new(
            "test-hive".to_string(),
            "A test hive".to_string(),
            "test-user".to_string(),
            temp_dir.path().to_path_buf(),
            (64, 64),
        ).unwrap();
        
        // Add tags
        hive.add_tag("important".to_string()).unwrap();
        hive.add_tag("test".to_string()).unwrap();
        
        assert_eq!(hive.metadata.tags.len(), 2);
        assert!(hive.metadata.tags.contains(&"important".to_string()));
        assert!(hive.metadata.tags.contains(&"test".to_string()));
        
        // Add properties
        hive.set_property("priority".to_string(), "high".to_string()).unwrap();
        hive.set_property("category".to_string(), "test".to_string()).unwrap();
        
        assert_eq!(hive.get_property("priority"), Some(&"high".to_string()));
        assert_eq!(hive.get_property("category"), Some(&"test".to_string()));
        
        // Remove a tag
        hive.remove_tag("important").unwrap();
        
        assert_eq!(hive.metadata.tags.len(), 1);
        assert!(hive.metadata.tags.contains(&"test".to_string()));
        
        // Remove a property
        hive.remove_property("priority").unwrap();
        
        assert_eq!(hive.get_property("priority"), None);
        assert_eq!(hive.get_property("category"), Some(&"test".to_string()));
    }
    
    #[test]
    fn test_hive_manager() {
        let temp_dir = tempdir().unwrap();
        let mut manager = HiveManager::new(temp_dir.path().to_path_buf());
        
        // Create a hive
        let hive_id = manager.create_hive(
            "test-hive".to_string(),
            "A test hive".to_string(),
            "test-user".to_string(),
            (64, 64),
        ).unwrap();
        
        // Get the hive
        let hive_arc = manager.get_hive(&hive_id).unwrap();
        let hive = hive_arc.read().unwrap();
        
        assert_eq!(hive.name, "test-hive");
        assert_eq!(hive.description, "A test hive");
        
        // Get by name
        let hive_arc2 = manager.get_hive_by_name("test-hive").unwrap();
        let hive2 = hive_arc2.read().unwrap();
        
        assert_eq!(hive2.id, hive_id);
        
        // List hives
        let hives = manager.list_hives();
        
        assert_eq!(hives.len(), 1);
        assert_eq!(hives[0].0, hive_id);
        assert_eq!(hives[0].1, "test-hive");
    }
}
