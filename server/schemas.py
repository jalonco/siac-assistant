"""
SIAC Assistant - Pydantic Schemas and Data Models

This module contains all the Pydantic models and Enum classes that represent
the database schema for the SIAC Assistant application.
"""

from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


# ============================================================================
# ENUMERATION CLASSES
# ============================================================================

class TemplateCategory(str, Enum):
    """
    Enumeration for message template categories.
    
    Values:
        MARKETING: Marketing-related templates
        UTILITY: Utility/functional templates
        AUTHENTICATION: Authentication-related templates
    """
    MARKETING = "Marketing"
    UTILITY = "Utility"
    AUTHENTICATION = "Authentication"


class PhoneStatus(str, Enum):
    """
    Enumeration for WhatsApp phone number status.
    
    Values:
        CONNECTED: Phone number is connected and active
        DISCONNECTED: Phone number is disconnected
        IN_REVIEW: Phone number is under review
    """
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    IN_REVIEW = "IN_REVIEW"


class TemplateStatus(str, Enum):
    """
    Enumeration for message template approval status.
    
    Values:
        PENDING: Template is pending approval
        APPROVED: Template has been approved
        REJECTED: Template has been rejected
        PAUSED: Template is paused
    """
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PAUSED = "PAUSED"


class QualityScore(str, Enum):
    """
    Enumeration for template quality scores.
    
    These ratings affect Template Pacing and Pausing.
    
    Values:
        GREEN: High quality score
        YELLOW: Medium quality score
        RED: Low quality score
        UNKNOWN: Quality score not determined (corresponds to 'Active - Quality pending')
    """
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    UNKNOWN = "UNKNOWN"


class CampaignStatus(str, Enum):
    """
    Enumeration for campaign execution status.
    
    Values:
        COMPLETED: Campaign has completed successfully
        PAUSED_META: Campaign is paused by Meta
        RUNNING: Campaign is currently running
        FAILED: Campaign has failed
    """
    COMPLETED = "COMPLETED"
    PAUSED_META = "PAUSED_META"
    RUNNING = "RUNNING"
    FAILED = "FAILED"


class DeliveryStatus(str, Enum):
    """
    Enumeration for message delivery status.
    
    Values:
        SENT: Message has been sent
        DELIVERED: Message has been delivered
        FAILED: Message delivery failed
    """
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class PacingStatus(str, Enum):
    """
    Enumeration for message pacing status.
    
    Values:
        ACCEPTED: Message pacing accepted
        HELD_FOR_QUALITY_ASSESSMENT: Message held for quality assessment
    """
    ACCEPTED = "accepted"
    HELD_FOR_QUALITY_ASSESSMENT = "held_for_quality_assessment"


# ============================================================================
# PYDANTIC BASE MODELS
# ============================================================================

class UserBase(BaseModel):
    """
    Base model for User entity.
    
    Attributes:
        username: Unique username for the user
        client_id: Foreign key reference to the client
    """
    username: str = Field(..., description="Unique username for the user")
    client_id: UUID = Field(..., description="Foreign key reference to the client")


class UserCreate(UserBase):
    """Model for creating a new user."""
    pass


class UserUpdate(BaseModel):
    """
    Model for updating user information.
    
    Attributes:
        username: Updated username (optional)
    """
    username: Optional[str] = Field(None, description="Updated username")


class User(UserBase):
    """
    Complete User model with primary key.
    
    Attributes:
        user_id: Primary key UUID for the user
        username: Unique username for the user
        client_id: Foreign key reference to the client
    """
    user_id: UUID = Field(..., description="Primary key UUID for the user")
    
    class Config:
        from_attributes = True


class ClientBase(BaseModel):
    """
    Base model for Client entity.
    
    Attributes:
        name: Client name
        meta_waba_id: Meta WhatsApp Business Account ID (UNIQUE and NOT NULL)
        meta_access_token: Meta access token for API calls
        billing_email: Client billing email address
    """
    name: str = Field(..., description="Client name")
    meta_waba_id: str = Field(..., description="Meta WhatsApp Business Account ID (UNIQUE and NOT NULL)")
    meta_access_token: str = Field(..., description="Meta access token for API calls")
    billing_email: str = Field(..., description="Client billing email address")


class ClientCreate(ClientBase):
    """Model for creating a new client."""
    pass


class ClientUpdate(BaseModel):
    """
    Model for updating client information.
    
    Attributes:
        name: Updated client name (optional)
        meta_waba_id: Updated Meta WABA ID (optional)
        meta_access_token: Updated Meta access token (optional)
        billing_email: Updated billing email (optional)
    """
    name: Optional[str] = Field(None, description="Updated client name")
    meta_waba_id: Optional[str] = Field(None, description="Updated Meta WABA ID")
    meta_access_token: Optional[str] = Field(None, description="Updated Meta access token")
    billing_email: Optional[str] = Field(None, description="Updated billing email")


class Client(ClientBase):
    """
    Complete Client model with primary key.
    
    Attributes:
        client_id: Primary key UUID for the client
        name: Client name
        meta_waba_id: Meta WhatsApp Business Account ID (UNIQUE and NOT NULL)
        meta_access_token: Meta access token for API calls
        billing_email: Client billing email address
    """
    client_id: UUID = Field(..., description="Primary key UUID for the client")
    
    class Config:
        from_attributes = True


class WhatsAppPhoneNumberBase(BaseModel):
    """
    Base model for WhatsApp Phone Number entity.
    
    Attributes:
        client_id: Foreign key reference to the client
        display_phone_number: Display phone number (unique)
        status: Phone status using PhoneStatus enum
        is_default: Whether this is the default phone number (default False)
        description: Description of the phone number
    """
    client_id: UUID = Field(..., description="Foreign key reference to the client")
    display_phone_number: str = Field(..., description="Display phone number (unique)")
    status: PhoneStatus = Field(..., description="Phone status using PhoneStatus enum")
    is_default: bool = Field(default=False, description="Whether this is the default phone number")
    description: str = Field(..., description="Description of the phone number")


class WhatsAppPhoneNumberCreate(WhatsAppPhoneNumberBase):
    """Model for creating a new WhatsApp phone number."""
    pass


class WhatsAppPhoneNumberUpdate(BaseModel):
    """
    Model for updating WhatsApp phone number information.
    
    Attributes:
        display_phone_number: Updated display phone number (optional)
        status: Updated phone status (optional)
        is_default: Updated default status (optional)
        description: Updated description (optional)
    """
    display_phone_number: Optional[str] = Field(None, description="Updated display phone number")
    status: Optional[PhoneStatus] = Field(None, description="Updated phone status")
    is_default: Optional[bool] = Field(None, description="Updated default status")
    description: Optional[str] = Field(None, description="Updated description")


class WhatsAppPhoneNumber(WhatsAppPhoneNumberBase):
    """
    Complete WhatsApp Phone Number model with primary key.
    
    Attributes:
        whatsapp_phone_number_id: Primary key string for the phone number (Meta WBPNID)
        client_id: Foreign key reference to the client
        display_phone_number: Display phone number (unique)
        status: Phone status using PhoneStatus enum
        is_default: Whether this is the default phone number
        description: Description of the phone number
    """
    whatsapp_phone_number_id: str = Field(..., description="Primary key string for the phone number (Meta WBPNID)")
    
    class Config:
        from_attributes = True


class MessageTemplateBase(BaseModel):
    """
    Base model for Message Template entity.
    
    Attributes:
        client_id: Foreign key reference to the client
        category: Template category using TemplateCategory enum
        meta_template_id: Meta template ID
        status: Template status using TemplateStatus enum
        quality_score: Quality score using QualityScore enum
    """
    client_id: UUID = Field(..., description="Foreign key reference to the client")
    category: TemplateCategory = Field(..., description="Template category using TemplateCategory enum")
    meta_template_id: str = Field(..., description="Meta template ID")
    status: TemplateStatus = Field(..., description="Template status using TemplateStatus enum")
    quality_score: QualityScore = Field(..., description="Quality score using QualityScore enum")


class MessageTemplateCreate(MessageTemplateBase):
    """Model for creating a new message template."""
    pass


class MessageTemplateUpdate(BaseModel):
    """
    Model for updating message template information.
    
    Attributes:
        category: Updated template category (optional)
        meta_template_id: Updated Meta template ID (optional)
        status: Updated template status (optional)
        quality_score: Updated quality score (optional)
    """
    category: Optional[TemplateCategory] = Field(None, description="Updated template category")
    meta_template_id: Optional[str] = Field(None, description="Updated Meta template ID")
    status: Optional[TemplateStatus] = Field(None, description="Updated template status")
    quality_score: Optional[QualityScore] = Field(None, description="Updated quality score")


class MessageTemplate(MessageTemplateBase):
    """
    Complete Message Template model with primary key.
    
    Attributes:
        template_id: Primary key UUID for the template
        client_id: Foreign key reference to the client
        category: Template category using TemplateCategory enum
        meta_template_id: Meta template ID
        status: Template status using TemplateStatus enum
        quality_score: Quality score using QualityScore enum
    """
    template_id: UUID = Field(..., description="Primary key UUID for the template")
    
    class Config:
        from_attributes = True


class CampaignBase(BaseModel):
    """
    Base model for Campaign entity.
    
    Attributes:
        client_id: Foreign key reference to the client
        template_id: Foreign key reference to the message template
        whatsapp_phone_number_id: Foreign key to the phone number used for sending
        initiated_by_user_id: Foreign key reference to the user who initiated the campaign
        total_recipients_planned: Total number of recipients planned for the campaign
        status: Campaign status using CampaignStatus enum
    """
    client_id: UUID = Field(..., description="Foreign key reference to the client")
    template_id: UUID = Field(..., description="Foreign key reference to the message template")
    whatsapp_phone_number_id: str = Field(..., description="Foreign key to the phone number used for sending")
    initiated_by_user_id: UUID = Field(..., description="Foreign key reference to the user who initiated the campaign")
    total_recipients_planned: int = Field(..., description="Total number of recipients planned for the campaign")
    status: CampaignStatus = Field(..., description="Campaign status using CampaignStatus enum")


class CampaignCreate(CampaignBase):
    """Model for creating a new campaign."""
    pass


class CampaignUpdate(BaseModel):
    """
    Model for updating campaign information.
    
    Attributes:
        template_id: Updated template reference (optional)
        whatsapp_phone_number_id: Updated phone number reference (optional)
        total_recipients_planned: Updated total recipients planned (optional)
        status: Updated campaign status (optional)
    """
    template_id: Optional[UUID] = Field(None, description="Updated template reference")
    whatsapp_phone_number_id: Optional[str] = Field(None, description="Updated phone number reference")
    total_recipients_planned: Optional[int] = Field(None, description="Updated total recipients planned")
    status: Optional[CampaignStatus] = Field(None, description="Updated campaign status")


class Campaign(CampaignBase):
    """
    Complete Campaign model with primary key.
    
    Attributes:
        campaign_id: Primary key UUID for the campaign
        client_id: Foreign key reference to the client
        template_id: Foreign key reference to the message template
        whatsapp_phone_number_id: Foreign key to the phone number used for sending
        initiated_by_user_id: Foreign key reference to the user who initiated the campaign
        total_recipients_planned: Total number of recipients planned for the campaign
        status: Campaign status using CampaignStatus enum
    """
    campaign_id: UUID = Field(..., description="Primary key UUID for the campaign")
    
    class Config:
        from_attributes = True


class MessageTransactionBase(BaseModel):
    """
    Base model for Message Transaction entity.
    
    Attributes:
        campaign_id: Foreign key reference to the campaign
        meta_message_id: Meta message ID (unique, for webhooks)
        whatsapp_phone_number_id: Foreign key to the phone number used
        template_category: Template category using TemplateCategory enum (for cost calculation)
        delivery_status: Delivery status using DeliveryStatus enum
        pacing_status: Pacing status using PacingStatus enum (for message retention by quality)
        meta_error_code: Meta error code (integer, e.g., 131049 for marketing limit per user)
        cost_unit_applied: Cost unit applied (Decimal, representing NUMERIC(10, 4))
        variable_payload_json: Variable payload JSON (Dict, for storing actual variable parameter values)
    """
    campaign_id: UUID = Field(..., description="Foreign key reference to the campaign")
    meta_message_id: str = Field(..., description="Meta message ID (unique, for webhooks)")
    whatsapp_phone_number_id: str = Field(..., description="Foreign key to the phone number used")
    template_category: TemplateCategory = Field(..., description="Template category using TemplateCategory enum (for cost calculation)")
    delivery_status: DeliveryStatus = Field(..., description="Delivery status using DeliveryStatus enum")
    pacing_status: PacingStatus = Field(..., description="Pacing status using PacingStatus enum (for message retention by quality)")
    meta_error_code: int = Field(..., description="Meta error code (integer, e.g., 131049 for marketing limit per user)")
    cost_unit_applied: Decimal = Field(..., description="Cost unit applied (Decimal, representing NUMERIC(10, 4))")
    variable_payload_json: Dict[str, Any] = Field(..., description="Variable payload JSON (Dict, for storing actual variable parameter values)")


class MessageTransactionCreate(MessageTransactionBase):
    """Model for creating a new message transaction."""
    pass


class MessageTransactionUpdate(BaseModel):
    """
    Model for updating message transaction information.
    
    Attributes:
        delivery_status: Updated delivery status (optional)
        pacing_status: Updated pacing status (optional)
        meta_error_code: Updated Meta error code (optional)
        cost_unit_applied: Updated cost unit applied (optional)
        variable_payload_json: Updated variable payload JSON (optional)
    """
    delivery_status: Optional[DeliveryStatus] = Field(None, description="Updated delivery status")
    pacing_status: Optional[PacingStatus] = Field(None, description="Updated pacing status")
    meta_error_code: Optional[int] = Field(None, description="Updated Meta error code")
    cost_unit_applied: Optional[Decimal] = Field(None, description="Updated cost unit applied")
    variable_payload_json: Optional[Dict[str, Any]] = Field(None, description="Updated variable payload JSON")


class MessageTransaction(MessageTransactionBase):
    """
    Complete Message Transaction model with primary key.
    
    Attributes:
        transaction_id: Primary key UUID for the transaction
        campaign_id: Foreign key reference to the campaign
        meta_message_id: Meta message ID (unique, for webhooks)
        whatsapp_phone_number_id: Foreign key to the phone number used
        template_category: Template category using TemplateCategory enum (for cost calculation)
        delivery_status: Delivery status using DeliveryStatus enum
        pacing_status: Pacing status using PacingStatus enum (for message retention by quality)
        meta_error_code: Meta error code (integer, e.g., 131049 for marketing limit per user)
        cost_unit_applied: Cost unit applied (Decimal, representing NUMERIC(10, 4))
        variable_payload_json: Variable payload JSON (Dict, for storing actual variable parameter values)
    """
    transaction_id: UUID = Field(..., description="Primary key UUID for the transaction")
    
    class Config:
        from_attributes = True
