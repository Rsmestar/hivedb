use hivedb::{core, init, name, version};
use log::{error, info};
use std::env;
use std::process;

/// Main entry point for the HiveDB CLI
fn main() {
    // Initialize the database system
    if let Err(e) = init() {
        error!("Failed to initialize HiveDB: {}", e);
        process::exit(1);
    }

    // Parse command line arguments
    let args: Vec<String> = env::args().collect();
    let command = if args.len() > 1 { &args[1] } else { "help" };

    match command {
        "version" => {
            println!("{} v{}", name(), version());
        }
        "start" => {
            info!("Starting HiveDB server...");
            if let Err(e) = start_server() {
                error!("Server error: {}", e);
                process::exit(1);
            }
        }
        "create" => {
            if args.len() < 3 {
                println!("Error: Missing hive name");
                print_usage();
                process::exit(1);
            }
            let hive_name = &args[2];
            info!("Creating new hive: {}", hive_name);
            if let Err(e) = create_hive(hive_name) {
                error!("Failed to create hive: {}", e);
                process::exit(1);
            }
            println!("✅ Hive '{}' created successfully", hive_name);
        }
        "help" | _ => {
            print_usage();
        }
    }
}

/// Start the HiveDB server
fn start_server() -> Result<(), Box<dyn std::error::Error>> {
    println!("🐝 {} v{} server started", name(), version());
    println!("Listening for connections...");
    
    // TODO: Implement actual server logic
    
    Ok(())
}

/// Create a new hive (database)
fn create_hive(name: &str) -> Result<(), Box<dyn std::error::Error>> {
    // TODO: Implement hive creation logic
    
    Ok(())
}

/// Print usage information
fn print_usage() {
    println!("🐝 {} v{}", name(), version());
    println!("نظام قواعد بيانات ثوري مستوحى من خلية النحل");
    println!();
    println!("USAGE:");
    println!("  hivedb [COMMAND] [OPTIONS]");
    println!();
    println!("COMMANDS:");
    println!("  start             Start the HiveDB server");
    println!("  create <name>     Create a new hive (database)");
    println!("  version           Display version information");
    println!("  help              Display this help message");
    println!();
    println!("For more information, visit: https://hivedb.example.com");
}
