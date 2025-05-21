// HiveDB: A revolutionary database system inspired by beehives
//
// This is the main library entry point that exposes the public API
// for the HiveDB database system.

pub mod core;
pub mod storage;
pub mod security;
pub mod network;
pub mod utils;

#[cfg(feature = "wasm")]
pub mod wasm;

use log::{info, LevelFilter};
use std::error::Error;

/// Initialize the HiveDB system with the given configuration
pub fn init() -> Result<(), Box<dyn Error>> {
    // Initialize logging
    env_logger::Builder::new()
        .filter_level(LevelFilter::Info)
        .init();
    
    info!("HiveDB initialized successfully");
    
    Ok(())
}

/// Version information for HiveDB
pub fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

/// Returns the name of the database system
pub fn name() -> &'static str {
    "HiveDB - نظام قواعد بيانات ثوري مستوحى من خلية النحل"
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version() {
        assert!(!version().is_empty());
    }

    #[test]
    fn test_name() {
        assert_eq!(
            name(),
            "HiveDB - نظام قواعد بيانات ثوري مستوحى من خلية النحل"
        );
    }
}
