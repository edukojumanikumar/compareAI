"""
Database Models Reference
For future integration with PostgreSQL and SQLAlchemy

NOTE: This is for reference only. Phase 1 does not include database integration.
Phase 2+ will implement these models with SQLAlchemy ORM.
"""

from typing import Optional, List
from datetime import datetime
from enum import Enum

# Status Enums
class InspectionStatus(str, Enum):
    PASS = "PASS"
    MINOR_ISSUES = "MINOR_ISSUES"
    REVIEW = "REVIEW"
    FAIL = "FAIL"


class PropertyType(str, Enum):
    AIRBNB = "AIRBNB"
    HOTEL = "HOTEL"
    VACATION_RENTAL = "VACATION_RENTAL"
    CAR_RENTAL = "CAR_RENTAL"
    OTHER = "OTHER"


class IssueSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Models (SQLAlchemy compatible)

class Property:
    """Property model - Represents a property (hotel, rental, etc.)"""
    
    __tablename__ = "properties"
    
    # Fields
    # id: Integer, Primary Key
    # name: String (required) - Property name
    # address: String - Full address
    # property_type: Enum - Type of property (AIRBNB, HOTEL, etc.)
    # owner_id: String - Owner/manager identifier
    # created_at: DateTime - Creation timestamp
    # updated_at: DateTime - Last update timestamp
    
    # Relationships
    # rooms: List[Room] - Rooms in this property
    # inspections: List[Inspection] - All inspections for this property
    
    pass


class Room:
    """Room model - Represents a room within a property"""
    
    __tablename__ = "rooms"
    
    # Fields
    # id: Integer, Primary Key
    # property_id: Integer, Foreign Key → Property.id
    # name: String - Room name (e.g., "Master Bedroom", "Suite 201")
    # room_type: String - Type of room
    # description: Text - Room description
    # capacity: Integer - Maximum occupancy
    # created_at: DateTime
    # updated_at: DateTime
    
    # Relationships
    # property: Property - Parent property
    # reference_images: List[ReferenceImage] - Reference images
    # inspections: List[Inspection] - All inspections
    
    pass


class ReferenceImage:
    """Reference Image model - Baseline image of room in ideal state"""
    
    __tablename__ = "reference_images"
    
    # Fields
    # id: Integer, Primary Key
    # room_id: Integer, Foreign Key → Room.id
    # image_url: String - S3/local storage path
    # image_hash: String - SHA-256 hash for deduplication
    # is_primary: Boolean - Is this the primary reference image?
    # created_at: DateTime
    # created_by: String - Staff member who uploaded
    # notes: Text - Optional notes about the image
    
    # Relationships
    # room: Room - Parent room
    
    pass


class Inspection:
    """Inspection model - Records an inspection comparison"""
    
    __tablename__ = "inspections"
    
    # Fields
    # id: Integer, Primary Key
    # room_id: Integer, Foreign Key → Room.id
    # reference_image_id: Integer, Foreign Key → ReferenceImage.id
    # inspection_image_url: String - S3/local storage path
    # score: Integer - Similarity score (0-100)
    # status: Enum - PASS/MINOR_ISSUES/REVIEW/FAIL
    # message: String - Human-readable result
    # change_percentage: Float - Percentage of pixels changed
    # comparison_confidence: String - Confidence level (LOW/MEDIUM/HIGH)
    # created_at: DateTime
    # inspector_id: String - Staff member ID who performed inspection
    # notes: Text - Manual notes from inspector
    # metadata: JSON - Additional comparison data
    
    # Relationships
    # room: Room - Inspected room
    # reference_image: ReferenceImage - Reference used
    # issues: List[InspectionIssue] - Detected issues
    
    pass


class InspectionIssue:
    """Inspection Issue model - Specific issues detected in inspection"""
    
    __tablename__ = "inspection_issues"
    
    # Fields
    # id: Integer, Primary Key
    # inspection_id: Integer, Foreign Key → Inspection.id
    # issue_type: String - Category (CLEANLINESS, DAMAGE, MISSING_ITEM, etc.)
    # description: String - Description of issue
    # severity: Enum - LOW/MEDIUM/HIGH/CRITICAL
    # location: String - Where in room (optional coordinates)
    # resolution: String - How issue was resolved (if applicable)
    # resolved_at: DateTime - When issue was resolved
    # created_at: DateTime
    
    # Relationships
    # inspection: Inspection - Parent inspection
    
    pass


class InspectionHistory:
    """Inspection History model - Track inspection history for a room"""
    
    __tablename__ = "inspection_history"
    
    # Fields
    # id: Integer, Primary Key
    # room_id: Integer, Foreign Key → Room.id
    # inspection_id: Integer, Foreign Key → Inspection.id
    # previous_score: Integer - Previous inspection score
    # current_score: Integer - Current inspection score
    # score_trend: String - IMPROVING/DECLINING/STABLE
    # days_since_last_inspection: Integer
    # created_at: DateTime
    
    # Relationships
    # room: Room
    # inspection: Inspection
    
    pass


class ComparisonMetadata:
    """Comparison Metadata model - Detailed comparison metrics"""
    
    __tablename__ = "comparison_metadata"
    
    # Fields
    # id: Integer, Primary Key
    # inspection_id: Integer, Foreign Key → Inspection.id
    # overall_diff: Float - Average color difference
    # diff_l_channel: Float - Lightness channel difference
    # diff_a_channel: Float - Color A channel difference
    # diff_b_channel: Float - Color B channel difference
    # changed_pixels: Integer - Number of changed pixels
    # total_pixels: Integer - Total pixels in image
    # ssim_score: Float - Structural similarity score
    # features_matched: Integer - Number of SIFT features matched
    # homography_error: Float - Perspective transformation error
    # processing_time_ms: Float - Time to process comparison
    # created_at: DateTime
    
    # Relationships
    # inspection: Inspection
    
    pass


# Pydantic Models (for API validation - current use)

class ComparisonRequest:
    """Validation model for comparison request"""
    # reference_image: UploadFile
    # inspection_image: UploadFile
    pass


class ComparisonResponse:
    """Response model for comparison"""
    score: int  # 0-100
    status: InspectionStatus  # PASS, MINOR_ISSUES, REVIEW, FAIL
    message: str  # Human-readable message
    issues: List[str]  # Detected issues
    metadata: dict  # Additional data


class ValidationResponse:
    """Response model for image validation"""
    is_valid: bool
    quality_score: int  # 0-100
    blur_score: int
    brightness_score: int
    size_score: int
    issues: List[str]
    recommendations: List[str]


# Migration Plan for Phase 2+

"""
Database Setup Steps (Phase 2):

1. Create PostgreSQL database
   - CREATE DATABASE room_inspection;

2. Install SQLAlchemy
   - pip install sqlalchemy psycopg2-binary

3. Create database models using SQLAlchemy ORM
   - Use models defined above as reference

4. Create migration scripts
   - Use Alembic for schema versioning

5. Update API
   - Add database session management
   - Replace file-based storage with database

6. Add endpoints
   - GET /properties - List all properties
   - POST /properties - Create property
   - GET /rooms/{room_id}/inspections - Inspection history
   - GET /inspections/{id} - Get inspection details
   - etc.

7. Add analytics
   - Trending inspection scores
   - Issue patterns
   - Staff performance metrics

8. Add authentication
   - User management
   - Role-based access control
"""


# SQL Schema Reference (for manual creation if needed)

SQL_SCHEMA = """
-- Properties Table
CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    property_type VARCHAR(50),
    owner_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rooms Table
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    property_id INTEGER NOT NULL REFERENCES properties(id),
    name VARCHAR(255) NOT NULL,
    room_type VARCHAR(100),
    description TEXT,
    capacity INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reference Images Table
CREATE TABLE reference_images (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    image_url VARCHAR(500) NOT NULL,
    image_hash VARCHAR(64),
    is_primary BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    notes TEXT
);

-- Inspections Table
CREATE TABLE inspections (
    id SERIAL PRIMARY KEY,
    room_id INTEGER NOT NULL REFERENCES rooms(id),
    reference_image_id INTEGER NOT NULL REFERENCES reference_images(id),
    inspection_image_url VARCHAR(500) NOT NULL,
    score INTEGER,
    status VARCHAR(50),
    message TEXT,
    change_percentage NUMERIC(5, 2),
    comparison_confidence VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    inspector_id VARCHAR(100),
    notes TEXT,
    metadata JSONB
);

-- Inspection Issues Table
CREATE TABLE inspection_issues (
    id SERIAL PRIMARY KEY,
    inspection_id INTEGER NOT NULL REFERENCES inspections(id),
    issue_type VARCHAR(100),
    description TEXT,
    severity VARCHAR(50),
    location VARCHAR(255),
    resolution TEXT,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_rooms_property_id ON rooms(property_id);
CREATE INDEX idx_reference_images_room_id ON reference_images(room_id);
CREATE INDEX idx_inspections_room_id ON inspections(room_id);
CREATE INDEX idx_inspections_created_at ON inspections(created_at);
CREATE INDEX idx_issues_inspection_id ON inspection_issues(inspection_id);
"""
