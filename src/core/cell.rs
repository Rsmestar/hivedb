// HiveDB Cell Module
//
// This module defines the hexagonal cell structure that forms
// the foundation of our database storage system.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use crate::core::error::HiveError;
use hexgrid::{Coordinate, Direction, HexGrid};
use log::{debug, info};

/// Initialize the cell subsystem
pub fn init() -> Result<(), HiveError> {
    info!("Initializing hexagonal cell subsystem");
    // Initialize any global cell-related resources here
    Ok(())
}

/// Represents a single hexagonal cell in the database
///
/// Each cell contains data and metadata and is positioned
/// within a hexagonal grid structure.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Cell {
    /// Unique identifier for this cell
    pub id: String,
    
    /// Hexagonal coordinates within the grid
    pub coordinates: (i32, i32),
    
    /// The actual data stored in this cell
    pub data: CellData,
    
    /// Metadata about this cell
    pub metadata: CellMetadata,
    
    /// Links to neighboring cells
    pub neighbors: HashMap<Direction, String>,
}

/// The actual data stored in a cell
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CellData {
    /// The type of data stored in this cell
    pub data_type: CellDataType,
    
    /// The actual binary data, possibly compressed
    pub content: Vec<u8>,
    
    /// Whether the content is compressed
    pub is_compressed: bool,
    
    /// Checksum for data integrity
    pub checksum: String,
}

/// Types of data that can be stored in a cell
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum CellDataType {
    /// JSON document
    Json,
    
    /// Binary data
    Binary,
    
    /// Key-value pairs
    KeyValue,
    
    /// Index information
    Index,
    
    /// Schema definition
    Schema,
    
    /// Metadata about the hive
    HiveMetadata,
}

/// Metadata about a cell
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CellMetadata {
    /// When this cell was created
    pub created_at: u64,
    
    /// When this cell was last modified
    pub modified_at: u64,
    
    /// Size of the data in bytes
    pub size_bytes: usize,
    
    /// Version of this cell (for concurrency control)
    pub version: u64,
    
    /// Tags associated with this cell
    pub tags: Vec<String>,
}

impl Cell {
    /// Create a new cell with the given data
    pub fn new(
        id: String,
        coordinates: (i32, i32),
        data_type: CellDataType,
        content: Vec<u8>,
        compress: bool,
    ) -> Result<Self, HiveError> {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map_err(|_| HiveError::SystemTimeError)?
            .as_secs();
        
        let (final_content, is_compressed) = if compress {
            // Compress the data using LZ4
            let mut compressed = Vec::new();
            let mut encoder = lz4::EncoderBuilder::new()
                .level(6)
                .build(&mut compressed)
                .map_err(|e| HiveError::CompressionError(e.to_string()))?;
            
            std::io::copy(&mut &content[..], &mut encoder)
                .map_err(|e| HiveError::CompressionError(e.to_string()))?;
            
            let (_, result) = encoder.finish();
            result.map_err(|e| HiveError::CompressionError(e.to_string()))?;
            
            (compressed, true)
        } else {
            (content, false)
        };
        
        // Calculate checksum
        let checksum = format!("{:x}", ring::digest::digest(
            &ring::digest::SHA256,
            &final_content
        ));
        
        Ok(Self {
            id,
            coordinates,
            data: CellData {
                data_type,
                content: final_content,
                is_compressed,
                checksum,
            },
            metadata: CellMetadata {
                created_at: now,
                modified_at: now,
                size_bytes: final_content.len(),
                version: 1,
                tags: Vec::new(),
            },
            neighbors: HashMap::new(),
        })
    }
    
    /// Get the decompressed content of this cell
    pub fn get_content(&self) -> Result<Vec<u8>, HiveError> {
        if !self.data.is_compressed {
            return Ok(self.data.content.clone());
        }
        
        // Decompress the data
        let mut decoder = lz4::Decoder::new(&self.data.content[..])
            .map_err(|e| HiveError::DecompressionError(e.to_string()))?;
        
        let mut decompressed = Vec::new();
        std::io::copy(&mut decoder, &mut decompressed)
            .map_err(|e| HiveError::DecompressionError(e.to_string()))?;
        
        Ok(decompressed)
    }
    
    /// Update the content of this cell
    pub fn update_content(
        &mut self,
        new_content: Vec<u8>,
        compress: bool,
    ) -> Result<(), HiveError> {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map_err(|_| HiveError::SystemTimeError)?
            .as_secs();
        
        let (final_content, is_compressed) = if compress {
            // Compress the data using LZ4
            let mut compressed = Vec::new();
            let mut encoder = lz4::EncoderBuilder::new()
                .level(6)
                .build(&mut compressed)
                .map_err(|e| HiveError::CompressionError(e.to_string()))?;
            
            std::io::copy(&mut &new_content[..], &mut encoder)
                .map_err(|e| HiveError::CompressionError(e.to_string()))?;
            
            let (_, result) = encoder.finish();
            result.map_err(|e| HiveError::CompressionError(e.to_string()))?;
            
            (compressed, true)
        } else {
            (new_content, false)
        };
        
        // Calculate new checksum
        let checksum = format!("{:x}", ring::digest::digest(
            &ring::digest::SHA256,
            &final_content
        ));
        
        // Update the cell
        self.data.content = final_content;
        self.data.is_compressed = is_compressed;
        self.data.checksum = checksum;
        self.metadata.modified_at = now;
        self.metadata.size_bytes = self.data.content.len();
        self.metadata.version += 1;
        
        Ok(())
    }
    
    /// Add a tag to this cell
    pub fn add_tag(&mut self, tag: String) {
        if !self.metadata.tags.contains(&tag) {
            self.metadata.tags.push(tag);
        }
    }
    
    /// Remove a tag from this cell
    pub fn remove_tag(&mut self, tag: &str) {
        self.metadata.tags.retain(|t| t != tag);
    }
    
    /// Link this cell to a neighbor
    pub fn link_neighbor(&mut self, direction: Direction, neighbor_id: String) {
        self.neighbors.insert(direction, neighbor_id);
    }
    
    /// Unlink a neighbor
    pub fn unlink_neighbor(&mut self, direction: Direction) {
        self.neighbors.remove(&direction);
    }
}

/// A grid of hexagonal cells
pub struct CellGrid {
    /// The underlying hexagonal grid
    grid: HexGrid<Arc<RwLock<Cell>>>,
    
    /// Dimensions of the grid
    dimensions: (usize, usize),
}

impl CellGrid {
    /// Create a new empty cell grid
    pub fn new(dimensions: (usize, usize)) -> Self {
        Self {
            grid: HexGrid::new(),
            dimensions,
        }
    }
    
    /// Add a cell to the grid
    pub fn add_cell(&mut self, cell: Cell) -> Result<(), HiveError> {
        let coords = Coordinate::new(cell.coordinates.0, cell.coordinates.1);
        
        // Check if the coordinates are within bounds
        if cell.coordinates.0 < 0 || cell.coordinates.0 >= self.dimensions.0 as i32 ||
           cell.coordinates.1 < 0 || cell.coordinates.1 >= self.dimensions.1 as i32 {
            return Err(HiveError::OutOfBoundsError);
        }
        
        // Check if a cell already exists at these coordinates
        if self.grid.get(&coords).is_some() {
            return Err(HiveError::CellAlreadyExists);
        }
        
        // Add the cell to the grid
        self.grid.insert(coords, Arc::new(RwLock::new(cell)));
        
        // Update neighbor links
        self.update_neighbor_links(&coords);
        
        Ok(())
    }
    
    /// Get a cell from the grid
    pub fn get_cell(&self, coordinates: (i32, i32)) -> Option<Arc<RwLock<Cell>>> {
        let coords = Coordinate::new(coordinates.0, coordinates.1);
        self.grid.get(&coords).cloned()
    }
    
    /// Remove a cell from the grid
    pub fn remove_cell(&mut self, coordinates: (i32, i32)) -> Result<Cell, HiveError> {
        let coords = Coordinate::new(coordinates.0, coordinates.1);
        
        // Remove the cell
        let cell_arc = self.grid.remove(&coords)
            .ok_or(HiveError::CellNotFound)?;
        
        // Get exclusive access to the cell
        let cell = match Arc::try_unwrap(cell_arc) {
            Ok(lock) => lock.into_inner().map_err(|_| HiveError::LockError)?,
            Err(_) => return Err(HiveError::ReferenceError),
        };
        
        // Update neighbor links for adjacent cells
        for direction in Direction::all() {
            if let Some(neighbor_coords) = coords.neighbor(direction) {
                if let Some(neighbor_arc) = self.grid.get(&neighbor_coords) {
                    if let Ok(mut neighbor) = neighbor_arc.write() {
                        neighbor.unlink_neighbor(direction.opposite());
                    }
                }
            }
        }
        
        Ok(cell)
    }
    
    /// Update the neighbor links for a cell and its neighbors
    fn update_neighbor_links(&self, coords: &Coordinate) {
        if let Some(cell_arc) = self.grid.get(coords) {
            // For each direction, check if there's a neighbor
            for direction in Direction::all() {
                if let Some(neighbor_coords) = coords.neighbor(direction) {
                    if let Some(neighbor_arc) = self.grid.get(&neighbor_coords) {
                        // Get the IDs of both cells
                        let cell_id = if let Ok(cell) = cell_arc.read() {
                            cell.id.clone()
                        } else {
                            continue;
                        };
                        
                        let neighbor_id = if let Ok(neighbor) = neighbor_arc.read() {
                            neighbor.id.clone()
                        } else {
                            continue;
                        };
                        
                        // Update the links in both cells
                        if let Ok(mut cell) = cell_arc.write() {
                            cell.link_neighbor(direction, neighbor_id);
                        }
                        
                        if let Ok(mut neighbor) = neighbor_arc.write() {
                            neighbor.link_neighbor(direction.opposite(), cell_id);
                        }
                    }
                }
            }
        }
    }
    
    /// Get the number of cells in the grid
    pub fn cell_count(&self) -> usize {
        self.grid.len()
    }
    
    /// Get all cells in the grid
    pub fn all_cells(&self) -> Vec<Arc<RwLock<Cell>>> {
        self.grid.values().cloned().collect()
    }
    
    /// Find cells by tag
    pub fn find_by_tag(&self, tag: &str) -> Vec<Arc<RwLock<Cell>>> {
        self.grid.values()
            .filter(|cell_arc| {
                if let Ok(cell) = cell_arc.read() {
                    cell.metadata.tags.contains(&tag.to_string())
                } else {
                    false
                }
            })
            .cloned()
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_cell_creation() {
        let cell = Cell::new(
            "test-cell-1".to_string(),
            (0, 0),
            CellDataType::Json,
            b"{\"test\": \"data\"}".to_vec(),
            true,
        ).unwrap();
        
        assert_eq!(cell.id, "test-cell-1");
        assert_eq!(cell.coordinates, (0, 0));
        assert_eq!(cell.data.data_type, CellDataType::Json);
        assert!(cell.data.is_compressed);
        assert_eq!(cell.metadata.version, 1);
        assert!(cell.neighbors.is_empty());
    }
    
    #[test]
    fn test_cell_content() {
        let content = b"{\"test\": \"data\"}".to_vec();
        let cell = Cell::new(
            "test-cell-2".to_string(),
            (0, 0),
            CellDataType::Json,
            content.clone(),
            true,
        ).unwrap();
        
        // The content should be compressed
        assert!(cell.data.is_compressed);
        assert_ne!(cell.data.content, content);
        
        // But we should be able to get the original content back
        let decompressed = cell.get_content().unwrap();
        assert_eq!(decompressed, content);
    }
    
    #[test]
    fn test_cell_update() {
        let mut cell = Cell::new(
            "test-cell-3".to_string(),
            (0, 0),
            CellDataType::Json,
            b"{\"test\": \"data\"}".to_vec(),
            false,
        ).unwrap();
        
        let new_content = b"{\"test\": \"updated\"}".to_vec();
        cell.update_content(new_content.clone(), false).unwrap();
        
        assert_eq!(cell.get_content().unwrap(), new_content);
        assert_eq!(cell.metadata.version, 2);
    }
    
    #[test]
    fn test_cell_tags() {
        let mut cell = Cell::new(
            "test-cell-4".to_string(),
            (0, 0),
            CellDataType::Json,
            b"{\"test\": \"data\"}".to_vec(),
            false,
        ).unwrap();
        
        assert!(cell.metadata.tags.is_empty());
        
        cell.add_tag("important".to_string());
        cell.add_tag("test".to_string());
        
        assert_eq!(cell.metadata.tags.len(), 2);
        assert!(cell.metadata.tags.contains(&"important".to_string()));
        assert!(cell.metadata.tags.contains(&"test".to_string()));
        
        cell.remove_tag("important");
        
        assert_eq!(cell.metadata.tags.len(), 1);
        assert!(cell.metadata.tags.contains(&"test".to_string()));
    }
}
