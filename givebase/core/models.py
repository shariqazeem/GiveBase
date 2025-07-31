# models.py - Complete New Model System
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class DonationPool(models.Model):
    """Global donation pools instead of individual recipients"""
    POOL_TYPES = [
        ('emergency', '🚨 Emergency Fund'),
        ('community', '🏘️ Community Projects'), 
        ('creators', '🎨 Creator Support'),
        ('development', '⚡ Platform Development'),
    ]
    
    name = models.CharField(max_length=100)
    pool_type = models.CharField(max_length=20, choices=POOL_TYPES)
    description = models.TextField()
    wallet_address = models.CharField(max_length=42, unique=True)
    
    # Pool allocation percentage (0.0 to 1.0)
    allocation_percentage = models.DecimalField(max_digits=3, decimal_places=2, default=0.25)
    
    # Financial tracking
    total_raised = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0'))
    total_distributed = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0'))
    
    # Social features
    donor_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Visual
    emoji = models.CharField(max_length=10, default='💝')
    color = models.CharField(max_length=20, default='blue')
    image_url = models.URLField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.emoji} {self.name} - {self.total_raised} ETH"
    
    @property
    def progress_percentage(self):
        # For pools, we don't have a specific goal, so show activity level
        return min(int(self.donor_count * 2), 100)  # 50 donors = 100%


class UserProfile(models.Model):
    """Enhanced user profiles for social features"""
    wallet_address = models.CharField(max_length=42, unique=True, primary_key=True)
    
    # Social identities
    farcaster_username = models.CharField(max_length=100, blank=True)
    farcaster_fid = models.CharField(max_length=50, blank=True)
    ens_name = models.CharField(max_length=100, blank=True)
    
    # Profile info
    display_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True, max_length=280)
    avatar_url = models.URLField(blank=True)
    
    # Donation stats (denormalized for performance)
    total_donated = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0'))
    total_received = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0'))
    total_points = models.IntegerField(default=0)
    donation_count = models.IntegerField(default=0)
    
    # Social features
    is_public_profile = models.BooleanField(default=True)
    accepts_donations = models.BooleanField(default=True)
    donation_message = models.CharField(max_length=100, blank=True, default="Thanks for your support! 💙")
    
    # Token rewards
    tokens_earned = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0'))
    tokens_claimed = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0'))
    
    # Timestamps
    first_donation_date = models.DateTimeField(null=True, blank=True)
    last_donation_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.display_name or self.farcaster_username or self.wallet_address[:8]
    
    @property
    def display_identifier(self):
        if self.display_name:
            return self.display_name
        elif self.farcaster_username:
            return f"@{self.farcaster_username}"
        elif self.ens_name:
            return self.ens_name
        else:
            return f"{self.wallet_address[:6]}...{self.wallet_address[-4:]}"


class SocialDonation(models.Model):
    """Direct P2P donations between users"""
    donor_address = models.CharField(max_length=42, db_index=True)
    recipient_address = models.CharField(max_length=42, db_index=True)
    
    # Social context
    recipient_username = models.CharField(max_length=100, blank=True)
    recipient_fid = models.CharField(max_length=50, blank=True)
    
    # Donation details
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    message = models.TextField(blank=True, max_length=280)
    
    # Blockchain data
    tx_hash = models.CharField(max_length=66, unique=True)
    block_number = models.BigIntegerField(null=True, blank=True)
    
    # Social features
    is_public = models.BooleanField(default=True)
    frame_interaction = models.BooleanField(default=False)
    
    # Points and rewards
    points_earned = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['donor_address', '-created_at']),
            models.Index(fields=['recipient_address', '-created_at']),
            models.Index(fields=['is_public', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.donor_address[:8]}... → {self.recipient_address[:8]}... ({self.amount} ETH)"


class PoolDonation(models.Model):
    """Donations to global pools"""
    donor_address = models.CharField(max_length=42, db_index=True)
    pool = models.ForeignKey(DonationPool, on_delete=models.CASCADE, related_name='donations')
    
    # Donation details
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    
    # Blockchain data
    tx_hash = models.CharField(max_length=66, unique=True)
    block_number = models.BigIntegerField(null=True, blank=True)
    
    # Points and rewards
    points_earned = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['donor_address', '-created_at']),
            models.Index(fields=['pool', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.donor_address[:8]}... → {self.pool.name} ({self.amount} ETH)"


class TokenReward(models.Model):
    """Track token rewards for future airdrops"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    
    # Reward details
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    reason = models.CharField(max_length=100)  # 'donation', 'social_share', 'early_adopter'
    multiplier = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    
    # Social context
    related_donation_tx = models.CharField(max_length=66, blank=True)
    frame_interaction = models.BooleanField(default=False)
    
    # Status
    is_claimed = models.BooleanField(default=False)
    claimed_at = models.DateTimeField(null=True, blank=True)
    claim_tx_hash = models.CharField(max_length=66, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} - {self.amount} $GIVE ({self.reason})"


# Keep the original models for migration compatibility
class Recipient(models.Model):
    """Legacy model - will be migrated to pools"""
    CATEGORY_CHOICES = [
        ('homeless', 'Homeless Individual'),
        ('student', 'Student in Crisis'),
        ('medical', 'Medical Emergency'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    wallet_address = models.CharField(max_length=42, unique=True)
    
    # Keep for migration
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    goal_amount = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0.1'))
    raised_amount = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"[LEGACY] {self.name}"


class Donation(models.Model):
    """Legacy model - will be migrated"""
    donor_address = models.CharField(max_length=42, db_index=True)
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, related_name='donations', null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    tx_hash = models.CharField(max_length=66, unique=True)
    block_number = models.BigIntegerField(null=True, blank=True)
    points_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Migration helper fields
    migrated_to_pool = models.BooleanField(default=False)
    migrated_to_social = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"[LEGACY] {self.donor_address[:8]}... donated {self.amount} ETH"


class DonorProfile(models.Model):
    """Legacy model - will be migrated to UserProfile"""
    wallet_address = models.CharField(max_length=42, unique=True, primary_key=True)
    ens_name = models.CharField(max_length=100, blank=True)
    total_donated = models.DecimalField(max_digits=18, decimal_places=8, default=Decimal('0'))
    total_points = models.IntegerField(default=0)
    donation_count = models.IntegerField(default=0)
    is_public = models.BooleanField(default=True)
    first_donation_date = models.DateTimeField(null=True, blank=True)
    last_donation_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Migration flag
    migrated_to_user_profile = models.BooleanField(default=False)
    
    def __str__(self):
        return f"[LEGACY] {self.wallet_address[:8]}"