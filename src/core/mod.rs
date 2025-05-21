// HiveDB Core Module
//
// This module contains the core components of the HiveDB system,
// including the hexagonal data structure and basic operations.

pub mod cell;
pub mod hive;
pub mod query;
pub mod schema;
pub mod error;

// Re-export important types
pub use cell::Cell;
pub use hive::Hive;
pub use query::Query;
pub use schema::Schema;
pub use error::HiveError;

use log::info;

/// Initialize the core components of HiveDB
pub fn init() -> Result<(), error::HiveError> {
    info!("Initializing HiveDB core components");
    
    // Initialize the hexagonal grid system
    cell::init()?;
    
    // Initialize the hive management system
    hive::init()?;
    
    info!("HiveDB core components initialized successfully");
    Ok(())
}

/// Core configuration for HiveDB
#[derive(Debug, Clone)]
pub struct Config {
    /// Maximum number of cells per hive
    pub max_cells_per_hive: usize,
    
    /// Default compression level (0-9)
    pub compression_level: u8,
    
    /// Enable swarm intelligence optimization
    pub enable_swarm_optimization: bool,
    
    /// Hexagonal grid dimensions
    pub grid_dimensions: (usize, usize),
}

impl Default for Config {
    fn default() -> Self {
        Self {
            max_cells_per_hive: 10_000,
            compression_level: 6,
            enable_swarm_optimization: true,
            grid_dimensions: (64, 64),
        }
    }
}

/// Create a new configuration with custom settings
pub fn new_config(
    max_cells: Option<usize>,
    compression: Option<u8>,
    swarm_opt: Option<bool>,
    dimensions: Option<(usize, usize)>,
) -> Config {
    let default = Config::default();
    
    Config {
        max_cells_per_hive: max_cells.unwrap_or(default.max_cells_per_hive),
        compression_level: compression.unwrap_or(default.compression_level),
        enable_swarm_optimization: swarm_opt.unwrap_or(default.enable_swarm_optimization),
        grid_dimensions: dimensions.unwrap_or(default.grid_dimensions),
    }
}
