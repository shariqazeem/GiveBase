from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    DonationPool, UserProfile, SocialDonation, PoolDonation, 
     Recipient, Donation, DonorProfile
)


# Custom admin actions
def activate_pools(modeladmin, request, queryset):
    queryset.update(is_active=True)
activate_pools.short_description = "Activate selected pools"

def deactivate_pools(modeladmin, request, queryset):
    queryset.update(is_active=False)
deactivate_pools.short_description = "Deactivate selected pools"

@admin.register(DonationPool)
class DonationPoolAdmin(admin.ModelAdmin):
    list_display = [
        'emoji_name', 'pool_type', 'total_raised_display', 
        'donor_count', 'allocation_percentage', 'is_active_display', 'created_at'
    ]
    list_filter = ['pool_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'wallet_address']
    readonly_fields = ['total_raised', 'total_distributed', 'donor_count', 'progress_percentage', 'created_at', 'updated_at']
    actions = [activate_pools, deactivate_pools]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'pool_type', 'description', 'emoji', 'color')
        }),
        ('Financial Settings', {
            'fields': ('wallet_address', 'allocation_percentage')
        }),
        ('Statistics (Read-only)', {
            'fields': ('total_raised', 'total_distributed', 'donor_count', 'progress_percentage'),
            'classes': ('collapse',)
        }),
        ('Status & Visual', {
            'fields': ('is_active', 'image_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def emoji_name(self, obj):
        return f"{obj.emoji} {obj.name}"
    emoji_name.short_description = "Pool Name"
    
    def total_raised_display(self, obj):
        return f"{obj.total_raised:.4f} ETH"
    total_raised_display.short_description = "Total Raised"
    total_raised_display.admin_order_field = 'total_raised'
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✅ Active</span>')
        return format_html('<span style="color: red;">❌ Inactive</span>')
    is_active_display.short_description = "Status"
    is_active_display.admin_order_field = 'is_active'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
    'display_identifier', 'total_donated_display', 'total_received_display', 
     'donation_count', 'is_public_profile'  
]
    list_filter = ['is_public_profile', 'accepts_donations', 'created_at']
    search_fields = ['wallet_address', 'display_name', 'farcaster_username', 'ens_name']
    readonly_fields = [
        'wallet_address', 'total_donated', 'total_received', 
        'donation_count',  
        'first_donation_date', 'last_donation_date', 'created_at'
    ]
    
    fieldsets = (
        ('Wallet Information', {
            'fields': ('wallet_address',)
        }),
        ('Profile Information', {
            'fields': ('display_name', 'farcaster_username', 'ens_name', 'bio', 'avatar_url')
        }),
        ('Social Settings', {
            'fields': ('is_public_profile', 'accepts_donations', 'donation_message')
        }),
        ('Statistics (Read-only)', {
            'fields': ('total_donated', 'total_received', 'donation_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps (Read-only)', {
            'fields': ('first_donation_date', 'last_donation_date', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_donated_display(self, obj):
        return f"{obj.total_donated:.4f} ETH"
    total_donated_display.short_description = "Total Donated"
    total_donated_display.admin_order_field = 'total_donated'
    
    def total_received_display(self, obj):
        return f"{obj.total_received:.4f} ETH"
    total_received_display.short_description = "Total Received"
    total_received_display.admin_order_field = 'total_received'
    

@admin.register(PoolDonation)
class PoolDonationAdmin(admin.ModelAdmin):
    list_display = [
        'donor_short', 'pool_name', 'amount_display', 
         'created_at', 'tx_hash_short'
    ]
    list_filter = ['pool', 'created_at']
    search_fields = ['donor_address', 'tx_hash', 'pool__name']
    readonly_fields = ['donor_address', 'pool', 'amount', 'tx_hash', 'block_number',  'created_at']
    
    def donor_short(self, obj):
        return f"{obj.donor_address[:6]}...{obj.donor_address[-4:]}"
    donor_short.short_description = "Donor"
    
    def pool_name(self, obj):
        return f"{obj.pool.emoji} {obj.pool.name}"
    pool_name.short_description = "Pool"
    
    def amount_display(self, obj):
        return f"{obj.amount:.4f} ETH"
    amount_display.short_description = "Amount"
    amount_display.admin_order_field = 'amount'
    
    def tx_hash_short(self, obj):
        return f"{obj.tx_hash[:10]}...{obj.tx_hash[-6:]}"
    tx_hash_short.short_description = "Transaction"

@admin.register(SocialDonation)
class SocialDonationAdmin(admin.ModelAdmin):
    list_display = [
        'donor_short', 'recipient_short', 'amount_display', 
         'is_public', 'frame_interaction', 'created_at'
    ]
    list_filter = ['is_public', 'frame_interaction', 'created_at']
    search_fields = ['donor_address', 'recipient_address', 'message', 'tx_hash']
    readonly_fields = [
        'donor_address', 'recipient_address', 'amount', 'tx_hash', 
        'block_number',  'created_at'
    ]
    
    def donor_short(self, obj):
        return f"{obj.donor_address[:6]}...{obj.donor_address[-4:]}"
    donor_short.short_description = "Donor"
    
    def recipient_short(self, obj):
        return f"{obj.recipient_address[:6]}...{obj.recipient_address[-4:]}"
    recipient_short.short_description = "Recipient"
    
    def amount_display(self, obj):
        return f"{obj.amount:.4f} ETH"
    amount_display.short_description = "Amount"
    amount_display.admin_order_field = 'amount'


# LEGACY MODELS (for backward compatibility)

@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'goal_amount', 'raised_amount', 'progress', 'is_verified', 'is_active']
    list_filter = ['category', 'is_verified', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'wallet_address']
    readonly_fields = ['raised_amount', 'created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Financial Information', {
            'fields': ('wallet_address', 'goal_amount', 'raised_amount')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def progress(self, obj):
        if obj.goal_amount > 0:
            percentage = (obj.raised_amount / obj.goal_amount) * 100
            return f"{percentage:.1f}%"
        return "0%"
    progress.short_description = "Progress"

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = [
        'donor_short', 'recipient_name', 'amount_display', 
        'created_at', 'tx_hash_short'
    ]
    list_filter = ['recipient', 'created_at']
    search_fields = ['donor_address', 'tx_hash', 'recipient__name']
    readonly_fields = ['donor_address', 'recipient', 'amount', 'tx_hash', 'block_number',  'created_at']
    
    def donor_short(self, obj):
        return f"{obj.donor_address[:6]}...{obj.donor_address[-4:]}"
    donor_short.short_description = "Donor"
    
    def recipient_name(self, obj):
        return obj.recipient.name if obj.recipient else "Unknown"
    recipient_name.short_description = "Recipient"
    
    def amount_display(self, obj):
        return f"{obj.amount:.4f} ETH"
    amount_display.short_description = "Amount"
    amount_display.admin_order_field = 'amount'
    
    def tx_hash_short(self, obj):
        return f"{obj.tx_hash[:10]}...{obj.tx_hash[-6:]}"
    tx_hash_short.short_description = "Transaction"

@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = [
        'wallet_short', 'total_donated_display', 
        'donation_count', 'is_public', 'last_donation_date'
    ]
    list_filter = ['is_public', 'created_at']
    search_fields = ['wallet_address', 'ens_name']
    readonly_fields = [
        'wallet_address', 'total_donated', 'donation_count',
        'first_donation_date', 'last_donation_date', 'created_at'
    ]
    
    def wallet_short(self, obj):
        return f"{obj.wallet_address[:6]}...{obj.wallet_address[-4:]}"
    wallet_short.short_description = "Wallet"
    
    def total_donated_display(self, obj):
        return f"{obj.total_donated:.4f} ETH"
    total_donated_display.short_description = "Total Donated"
    total_donated_display.admin_order_field = 'total_donated'

# Customize admin site
admin.site.site_header = "GiveBase Administration"
admin.site.site_title = "GiveBase Admin"
admin.site.index_title = "Welcome to GiveBase Administration"