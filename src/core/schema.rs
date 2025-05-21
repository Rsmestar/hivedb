// HiveDB Schema Module
//
// This module defines the schema system for HiveDB, which allows
// for structured data validation and organization.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use crate::core::error::HiveError;

/// Represents a schema for data in HiveDB
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Schema {
    /// Name of this schema
    pub name: String,
    
    /// Description of this schema
    pub description: String,
    
    /// Version of this schema
    pub version: String,
    
    /// Fields defined in this schema
    pub fields: Vec<SchemaField>,
    
    /// Indexes for this schema
    pub indexes: Vec<SchemaIndex>,
    
    /// Additional metadata
    pub metadata: HashMap<String, String>,
}

/// Represents a field in a schema
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchemaField {
    /// Name of this field
    pub name: String,
    
    /// Description of this field
    pub description: String,
    
    /// Type of this field
    pub field_type: FieldType,
    
    /// Whether this field is required
    pub required: bool,
    
    /// Default value for this field
    pub default_value: Option<String>,
    
    /// Validation rules for this field
    pub validation: Vec<ValidationRule>,
}

/// Types of fields in a schema
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum FieldType {
    /// String value
    String,
    
    /// Integer value
    Integer,
    
    /// Floating-point value
    Float,
    
    /// Boolean value
    Boolean,
    
    /// Date/time value
    DateTime,
    
    /// Binary data
    Binary,
    
    /// Array of values
    Array(Box<FieldType>),
    
    /// Object with nested fields
    Object(Vec<SchemaField>),
    
    /// Reference to another cell
    Reference,
    
    /// Geospatial coordinates
    GeoPoint,
    
    /// Custom type
    Custom(String),
}

/// Validation rule for a field
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ValidationRule {
    /// Minimum length for strings or arrays
    MinLength(usize),
    
    /// Maximum length for strings or arrays
    MaxLength(usize),
    
    /// Pattern (regex) for strings
    Pattern(String),
    
    /// Minimum value for numbers
    MinValue(f64),
    
    /// Maximum value for numbers
    MaxValue(f64),
    
    /// Enumeration of allowed values
    Enum(Vec<String>),
    
    /// Custom validation rule
    Custom(String),
}

/// Index definition for a schema
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchemaIndex {
    /// Name of this index
    pub name: String,
    
    /// Fields included in this index
    pub fields: Vec<String>,
    
    /// Type of this index
    pub index_type: IndexType,
    
    /// Whether this index is unique
    pub unique: bool,
}

/// Types of indexes
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum IndexType {
    /// B-tree index
    BTree,
    
    /// Hash index
    Hash,
    
    /// Spatial index
    Spatial,
    
    /// Full-text search index
    FullText,
}

impl Schema {
    /// Create a new schema
    pub fn new(
        name: String,
        description: String,
        version: String,
    ) -> Self {
        Self {
            name,
            description,
            version,
            fields: Vec::new(),
            indexes: Vec::new(),
            metadata: HashMap::new(),
        }
    }
    
    /// Add a field to this schema
    pub fn add_field(&mut self, field: SchemaField) -> &mut Self {
        self.fields.push(field);
        self
    }
    
    /// Add an index to this schema
    pub fn add_index(&mut self, index: SchemaIndex) -> &mut Self {
        self.indexes.push(index);
        self
    }
    
    /// Set a metadata value
    pub fn set_metadata(&mut self, key: String, value: String) -> &mut Self {
        self.metadata.insert(key, value);
        self
    }
    
    /// Validate data against this schema
    pub fn validate(&self, data: &serde_json::Value) -> Result<(), HiveError> {
        // TODO: Implement schema validation
        
        Ok(())
    }
    
    /// Get a field by name
    pub fn get_field(&self, name: &str) -> Option<&SchemaField> {
        self.fields.iter().find(|f| f.name == name)
    }
    
    /// Get an index by name
    pub fn get_index(&self, name: &str) -> Option<&SchemaIndex> {
        self.indexes.iter().find(|i| i.name == name)
    }
}

impl SchemaField {
    /// Create a new schema field
    pub fn new(
        name: String,
        description: String,
        field_type: FieldType,
        required: bool,
    ) -> Self {
        Self {
            name,
            description,
            field_type,
            required,
            default_value: None,
            validation: Vec::new(),
        }
    }
    
    /// Set a default value for this field
    pub fn with_default(mut self, default_value: String) -> Self {
        self.default_value = Some(default_value);
        self
    }
    
    /// Add a validation rule to this field
    pub fn with_validation(mut self, rule: ValidationRule) -> Self {
        self.validation.push(rule);
        self
    }
}

impl SchemaIndex {
    /// Create a new schema index
    pub fn new(
        name: String,
        fields: Vec<String>,
        index_type: IndexType,
        unique: bool,
    ) -> Self {
        Self {
            name,
            fields,
            index_type,
            unique,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_schema_creation() {
        let mut schema = Schema::new(
            "user".to_string(),
            "User schema".to_string(),
            "1.0".to_string(),
        );
        
        // Add fields
        schema.add_field(
            SchemaField::new(
                "id".to_string(),
                "User ID".to_string(),
                FieldType::String,
                true,
            )
            .with_validation(ValidationRule::MinLength(3))
            .with_validation(ValidationRule::MaxLength(50))
        );
        
        schema.add_field(
            SchemaField::new(
                "name".to_string(),
                "User name".to_string(),
                FieldType::String,
                true,
            )
            .with_validation(ValidationRule::MinLength(1))
            .with_validation(ValidationRule::MaxLength(100))
        );
        
        schema.add_field(
            SchemaField::new(
                "age".to_string(),
                "User age".to_string(),
                FieldType::Integer,
                false,
            )
            .with_validation(ValidationRule::MinValue(0.0))
            .with_validation(ValidationRule::MaxValue(150.0))
        );
        
        // Add an index
        schema.add_index(
            SchemaIndex::new(
                "id_index".to_string(),
                vec!["id".to_string()],
                IndexType::BTree,
                true,
            )
        );
        
        // Set metadata
        schema.set_metadata("created_by".to_string(), "test".to_string());
        
        // Verify the schema
        assert_eq!(schema.name, "user");
        assert_eq!(schema.fields.len(), 3);
        assert_eq!(schema.indexes.len(), 1);
        assert_eq!(schema.metadata.get("created_by"), Some(&"test".to_string()));
        
        // Verify field retrieval
        let id_field = schema.get_field("id").unwrap();
        assert_eq!(id_field.name, "id");
        assert_eq!(id_field.required, true);
        
        // Verify index retrieval
        let id_index = schema.get_index("id_index").unwrap();
        assert_eq!(id_index.name, "id_index");
        assert_eq!(id_index.unique, true);
    }
}
