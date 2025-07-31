# urls.py - Complete URL Configuration for Global System
from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('app/', views.app, name='app'),
    
    # NEW GLOBAL SYSTEM ENDPOINTS
    
    # Donation Pools
    path('api/pools/', views.donation_pools, name='donation_pools'),
    path('api/donate-to-pool/', views.donate_to_pool, name='donate_to_pool'),
    
    # Social Donations (P2P)
    path('api/donate-to-user/', views.donate_to_user, name='donate_to_user'),
    path('api/social-feed/', views.social_feed, name='social_feed'),
    
    # User Profiles & Social Features
    path('api/user-profile/', views.user_profile_api, name='user_profile_api'),
    path('api/update-profile/', views.update_user_profile_api, name='update_user_profile_api'),
    
    # Statistics & Leaderboard
    path('api/stats/', views.stats, name='stats'),
    path('api/leaderboard/', views.leaderboard, name='leaderboard'),
    path('api/user-donations/', views.user_donations, name='user_donations'),
    
    # Token & Airdrop System
    path('api/token-rewards/', views.token_rewards, name='token_rewards'),
    path('api/airdrop-eligibility/', views.airdrop_eligibility, name='airdrop_eligibility'),
    
    # LEGACY ENDPOINTS (for backward compatibility)
    path('api/recipients/', views.recipients, name='recipients'),
    path('api/record-donation/', views.record_donation, name='record_donation'),
    
    # FUTURE FARCASTER ENDPOINTS (commented out until implemented)
    # path('frames/donate/', views.donation_frame, name='donation_frame'),
    # path('frames/profile/<str:username>/', views.profile_frame, name='profile_frame'),
    # path('frames/leaderboard/', views.leaderboard_frame, name='leaderboard_frame'),
]