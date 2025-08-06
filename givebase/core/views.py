# views.py - Updated API for Global Donation System
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from decimal import Decimal
import json
from datetime import datetime, timedelta
from .models import (
    DonationPool, SocialDonation, PoolDonation, UserProfile, 
    TokenReward, Donation, Recipient, DonorProfile  # Legacy models
)

# Main pages
def index(request):
    """Landing page"""
    return render(request, 'index.html')

def app(request):
    """Main dapp interface"""
    context = {
        'contract_address': '0x0000000000000000000000000000000000000000',
        'base_sepolia_rpc': 'https://sepolia.base.org',
        'chain_id': '0x14A34',
    }
    return render(request, 'app.html', context)

# NEW API ENDPOINTS

def donation_pools(request):
    """Get all active donation pools"""
    pools = DonationPool.objects.filter(is_active=True).order_by('pool_type')
    
    pools_data = []
    for pool in pools:
        pools_data.append({
            'id': pool.id,
            'name': pool.name,
            'pool_type': pool.pool_type,
            'description': pool.description,
            'emoji': pool.emoji,
            'color': pool.color,
            'wallet_address': pool.wallet_address,
            'total_raised': str(pool.total_raised),
            'donor_count': pool.donor_count,
            'allocation_percentage': str(pool.allocation_percentage),
            'image_url': pool.image_url,
            'progress_percentage': pool.progress_percentage,
        })
    
    return JsonResponse({'pools': pools_data})

@csrf_exempt
def donate_to_pool(request):
    """Record donation to a pool"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['donor_address', 'pool_id', 'amount', 'tx_hash']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing field: {field}'}, status=400)
            
            # Check for duplicate transaction
            if PoolDonation.objects.filter(tx_hash=data['tx_hash']).exists():
                return JsonResponse({'error': 'Donation already recorded'}, status=400)
            
            # Get pool
            try:
                pool = DonationPool.objects.get(id=data['pool_id'])
            except DonationPool.DoesNotExist:
                return JsonResponse({'error': 'Pool not found'}, status=404)
            
            # Create donation record
            donation_amount = Decimal(data['amount'])
            points_earned = calculate_points_and_tokens(donation_amount)
            
            donation = PoolDonation.objects.create(
                donor_address=data['donor_address'].lower(),
                pool=pool,
                amount=donation_amount,
                tx_hash=data['tx_hash'],
                block_number=data.get('block_number'),
                points_earned=points_earned
            )
            
            # Update pool stats
            pool.total_raised += donation_amount
            pool.donor_count = pool.donations.values('donor_address').distinct().count()
            pool.save()
            
            # Update user profile
            update_user_profile(data['donor_address'], donation_amount, points_earned, is_donor=True)
            
            # Create token reward
            create_token_reward(data['donor_address'], points_earned, 'pool_donation', data['tx_hash'])
            
            return JsonResponse({
                'success': True,
                'donation_id': donation.id,
                'points_earned': points_earned,
                'pool_name': pool.name,
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt  
def donate_to_user(request):
    """Record P2P donation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['donor_address', 'recipient_address', 'amount', 'tx_hash']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing field: {field}'}, status=400)
            
            # Check for duplicate transaction
            if SocialDonation.objects.filter(tx_hash=data['tx_hash']).exists():
                return JsonResponse({'error': 'Donation already recorded'}, status=400)
            
            # Create social donation record  
            donation_amount = Decimal(data['amount'])
            points_earned = calculate_points_and_tokens(donation_amount)
            
            # Social bonus for frame interactions
            if data.get('frame_interaction', False):
                points_earned = int(points_earned * 1.2)  # 20% bonus
            
            donation = SocialDonation.objects.create(
                donor_address=data['donor_address'].lower(),
                recipient_address=data['recipient_address'].lower(),
                recipient_username=data.get('recipient_username', ''),
                recipient_fid=data.get('recipient_fid', ''),
                amount=donation_amount,
                message=data.get('message', ''),
                tx_hash=data['tx_hash'],
                block_number=data.get('block_number'),
                is_public=data.get('is_public', True),
                frame_interaction=data.get('frame_interaction', False),
                points_earned=points_earned
            )
            
            # Update user profiles
            update_user_profile(data['donor_address'], donation_amount, points_earned, is_donor=True)
            update_user_profile(data['recipient_address'], Decimal('0'), 0, received_amount=donation_amount)
            
            # Create token rewards
            reward_type = 'social_donation_frame' if data.get('frame_interaction') else 'social_donation'
            create_token_reward(data['donor_address'], points_earned, reward_type, data['tx_hash'])
            
            return JsonResponse({
                'success': True,
                'donation_id': donation.id,
                'points_earned': points_earned,
                'social_bonus': data.get('frame_interaction', False),
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def social_feed(request):
    """Get public donation feed for social features"""
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 20))
    
    # Get public social donations
    recent_donations = SocialDonation.objects.filter(
        is_public=True
    ).order_by('-created_at')
    
    paginator = Paginator(recent_donations, limit)
    donations_page = paginator.page(page)
    
    feed_data = []
    for donation in donations_page:
        # Get donor and recipient profiles
        donor_profile = UserProfile.objects.filter(wallet_address=donation.donor_address).first()
        recipient_profile = UserProfile.objects.filter(wallet_address=donation.recipient_address).first()
        
        feed_data.append({
            'id': donation.id,
            'donor': {
                'address': donation.donor_address,
                'display_name': donor_profile.display_identifier if donor_profile else None,
                'avatar_url': donor_profile.avatar_url if donor_profile else None,
            },
            'recipient': {
                'address': donation.recipient_address,
                'display_name': recipient_profile.display_identifier if recipient_profile else None,
                'username': donation.recipient_username,
                'avatar_url': recipient_profile.avatar_url if recipient_profile else None,
            },
            'amount': str(donation.amount),
            'message': donation.message,
            'points_earned': donation.points_earned,
            'frame_interaction': donation.frame_interaction,
            'time_ago': get_time_ago(donation.created_at),
            'tx_hash': donation.tx_hash,
        })
    
    return JsonResponse({
        'feed': feed_data,
        'pagination': {
            'current_page': page,
            'total_pages': paginator.num_pages,
            'has_next': donations_page.has_next(),
            'has_previous': donations_page.has_previous(),
        }
    })

def user_profile_api(request):
    """Get user profile for social features"""
    wallet_address = request.GET.get('address', '').lower()
    
    if not wallet_address:
        return JsonResponse({'error': 'Address required'}, status=400)
    
    try:
        profile = UserProfile.objects.get(wallet_address=wallet_address)
        
        # Get recent donation activity
        recent_donated = SocialDonation.objects.filter(
            donor_address=wallet_address
        ).order_by('-created_at')[:5]
        
        recent_received = SocialDonation.objects.filter(
            recipient_address=wallet_address
        ).order_by('-created_at')[:5]
        
        return JsonResponse({
            'address': profile.wallet_address,
            'display_name': profile.display_name,
            'farcaster_username': profile.farcaster_username,
            'ens_name': profile.ens_name,
            'bio': profile.bio,
            'avatar_url': profile.avatar_url,
            'donation_message': profile.donation_message,
            'total_donated': str(profile.total_donated),
            'total_received': str(profile.total_received),
            'total_points': profile.total_points,
            'tokens_earned': str(profile.tokens_earned),
            'accepts_donations': profile.accepts_donations,
            'is_public': profile.is_public_profile,
            'stats': {
                'donations_made': profile.donation_count,
                'donations_received': recent_received.count(),
                'first_donation': profile.first_donation_date.isoformat() if profile.first_donation_date else None,
                'last_donation': profile.last_donation_date.isoformat() if profile.last_donation_date else None,
            },
            'recent_activity': {
                'donated': [
                    {
                        'amount': str(d.amount),
                        'recipient': d.recipient_username or (d.recipient_address[:6] + '...' + d.recipient_address[-4:]),
                        'time_ago': get_time_ago(d.created_at)
                    } for d in recent_donated
                ],
                'received': [
                    {
                        'amount': str(d.amount),
                        'donor': d.donor_address[:6] + '...' + d.donor_address[-4:],
                        'message': d.message,
                        'time_ago': get_time_ago(d.created_at)
                    } for d in recent_received
                ]
            }
        })
        
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'address': wallet_address,
            'exists': False,
            'display_name': None,
            'accepts_donations': True,  # Default for new users
        })

@csrf_exempt
def update_user_profile_api(request):
    """Update user profile"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            wallet_address = data.get('wallet_address', '').lower()
            
            if not wallet_address:
                return JsonResponse({'error': 'Wallet address required'}, status=400)
            
            profile, created = UserProfile.objects.get_or_create(
                wallet_address=wallet_address
            )
            
            # Update fields
            if 'display_name' in data:
                profile.display_name = data['display_name'][:100]
            if 'bio' in data:
                profile.bio = data['bio'][:280]
            if 'donation_message' in data:
                profile.donation_message = data['donation_message'][:100]
            if 'accepts_donations' in data:
                profile.accepts_donations = data['accepts_donations']
            if 'is_public_profile' in data:
                profile.is_public_profile = data['is_public_profile']
            if 'farcaster_username' in data:
                profile.farcaster_username = data['farcaster_username'][:100]
            if 'avatar_url' in data:
                profile.avatar_url = data['avatar_url']
            
            profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def stats(request):
    """Get platform statistics"""
    user_address = request.GET.get('user', '').lower()
    
    # Platform stats - combine legacy and new data
    total_donated_legacy = Donation.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    total_donated_pools = PoolDonation.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    total_donated_social = SocialDonation.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    total_donated = total_donated_legacy + total_donated_pools + total_donated_social
    
    total_donors = UserProfile.objects.filter(total_donated__gt=0).count()
    total_recipients_legacy = Recipient.objects.filter(is_verified=True).count()
    active_pools = DonationPool.objects.filter(is_active=True).count()
    total_donations = (Donation.objects.count() + 
                      PoolDonation.objects.count() + 
                      SocialDonation.objects.count())
    
    # User-specific stats
    user_points = 0
    user_stats = None
    
    if user_address:
        try:
            user_profile = UserProfile.objects.get(wallet_address=user_address)
            user_points = user_profile.total_points
            user_stats = {
                'total_donated': str(user_profile.total_donated),
                'total_received': str(user_profile.total_received),
                'total_points': user_profile.total_points,
                'donation_count': user_profile.donation_count,
                'tokens_earned': str(user_profile.tokens_earned),
                'rank': get_user_rank(user_address)
            }
        except UserProfile.DoesNotExist:
            pass
    
    return JsonResponse({
        'total_donated': str(total_donated),
        'total_donors': total_donors,
        'total_recipients': total_recipients_legacy + active_pools,  # Legacy recipients + pools
        'total_donations': total_donations,
        'active_pools': active_pools,
        'user_points': user_points,
        'user_stats': user_stats,
    })

def leaderboard(request):
    """Get top donors leaderboard"""
    user_address = request.GET.get('user', '').lower()
    
    # Get top donors from UserProfile
    top_donors = UserProfile.objects.filter(
        is_public_profile=True,
        total_points__gt=0
    ).order_by('-total_points', '-total_donated')[:100]
    
    leaderboard_data = []
    user_position = None
    
    for i, donor in enumerate(top_donors):
        donor_data = {
            'rank': i + 1,
            'address': donor.wallet_address,
            'display_name': donor.display_identifier,
            'ens_name': donor.ens_name,
            'avatar_url': donor.avatar_url,
            'total_donated': str(donor.total_donated),
            'total_received': str(donor.total_received),
            'total_points': donor.total_points,
            'donation_count': donor.donation_count,
            'is_current_user': False
        }
        
        if user_address and donor.wallet_address.lower() == user_address:
            donor_data['is_current_user'] = True
            user_position = donor_data
        
        leaderboard_data.append(donor_data)
    
    # If user not in top 100, find their position
    if user_address and not user_position:
        try:
            user_profile = UserProfile.objects.get(wallet_address=user_address)
            rank = get_user_rank(user_address)
            
            user_position = {
                'rank': rank,
                'address': user_profile.wallet_address,
                'display_name': user_profile.display_identifier,
                'ens_name': user_profile.ens_name,
                'avatar_url': user_profile.avatar_url,
                'total_donated': str(user_profile.total_donated),
                'total_received': str(user_profile.total_received),
                'total_points': user_profile.total_points,
                'donation_count': user_profile.donation_count,
                'is_current_user': True
            }
        except UserProfile.DoesNotExist:
            pass
    
    return JsonResponse({
        'leaderboard': leaderboard_data,
        'user_position': user_position
    })

def user_donations(request):
    """Get user's donation history - both pool and social donations"""
    user_address = request.GET.get('user', '').lower()
    page = int(request.GET.get('page', 1))
    
    if not user_address:
        return JsonResponse({'error': 'User address required'}, status=400)
    
    # Get user stats
    user_stats = get_user_stats(user_address)
    
    # Get all donations (pool + social + legacy)
    pool_donations = PoolDonation.objects.filter(
        donor_address=user_address
    ).select_related('pool')
    
    social_donations = SocialDonation.objects.filter(
        donor_address=user_address
    )
    
    legacy_donations = Donation.objects.filter(
        donor_address=user_address
    ).select_related('recipient')
    
    # Combine and sort by date
    all_donations = []
    
    # Add pool donations
    for donation in pool_donations:
        all_donations.append({
            'type': 'pool',
            'id': donation.id,
            'recipient_name': donation.pool.name,
            'recipient_category': donation.pool.pool_type,
            'amount': str(donation.amount),
            'points_earned': donation.points_earned,
            'tx_hash': donation.tx_hash,
            'created_at': donation.created_at,
            'emoji': donation.pool.emoji,
        })
    
    # Add social donations
    for donation in social_donations:
        recipient_profile = UserProfile.objects.filter(wallet_address=donation.recipient_address).first()
        recipient_name = (recipient_profile.display_identifier if recipient_profile 
                         else donation.recipient_username or 
                         f"{donation.recipient_address[:6]}...{donation.recipient_address[-4:]}")
        
        all_donations.append({
            'type': 'social',
            'id': donation.id,
            'recipient_name': recipient_name,
            'recipient_category': 'user',
            'recipient_address': donation.recipient_address,
            'amount': str(donation.amount),
            'points_earned': donation.points_earned,
            'tx_hash': donation.tx_hash,
            'created_at': donation.created_at,
            'message': donation.message,
            'frame_interaction': donation.frame_interaction,
            'emoji': '👤',
        })
    
    # Add legacy donations
    for donation in legacy_donations:
        all_donations.append({
            'type': 'legacy',
            'id': donation.id,
            'recipient_name': donation.recipient.name if donation.recipient else 'Unknown',
            'recipient_category': donation.recipient.category if donation.recipient else 'unknown',
            'amount': str(donation.amount),
            'points_earned': donation.points_earned,
            'tx_hash': donation.tx_hash,
            'created_at': donation.created_at,
            'emoji': '📍',
        })
    
    # Sort by date
    all_donations.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Paginate
    paginator = Paginator(all_donations, 20)
    try:
        donations_page = paginator.page(page)
    except:
        donations_page = paginator.page(1)
    
    # Format donations for response
    donations_data = []
    for donation in donations_page:
        donations_data.append({
            'id': donation['id'],
            'type': donation['type'],
            'recipient_name': donation['recipient_name'],
            'recipient_category': donation['recipient_category'],
            'recipient_address': donation.get('recipient_address'),
            'amount': donation['amount'],
            'points_earned': donation['points_earned'],
            'tx_hash': donation['tx_hash'],
            'time_ago': get_time_ago(donation['created_at']),
            'message': donation.get('message', ''),
            'frame_interaction': donation.get('frame_interaction', False),
            'emoji': donation['emoji'],
        })
    
    return JsonResponse({
        'donations': donations_data,
        'user_stats': user_stats,
        'pagination': {
            'current_page': donations_page.number,
            'total_pages': paginator.num_pages,
            'has_next': donations_page.has_next(),
            'has_previous': donations_page.has_previous(),
        }
    })

# LEGACY API ENDPOINTS (for backward compatibility)

def recipients(request):
    """Legacy endpoint - now returns pools + legacy recipients"""
    # Get active pools as "recipients"
    pools = DonationPool.objects.filter(is_active=True)
    legacy_recipients = Recipient.objects.filter(is_verified=True, is_active=True)
    
    recipients_data = []
    
    # Add pools as recipients
    for pool in pools:
        recipients_data.append({
            'id': f"pool_{pool.id}",
            'name': f"{pool.emoji} {pool.name}",
            'category': pool.pool_type,
            'description': pool.description,
            'wallet_address': pool.wallet_address,
            'goal_amount': "1.0",  # Pools don't have specific goals
            'raised_amount': str(pool.total_raised),
            'verification_proof': f"Global Pool - {pool.donor_count} donors",
            'image_url': pool.image_url,
            'location': "Global",
            'urgency_level': 3,
            'progress_percentage': pool.progress_percentage,
            'created_at': pool.created_at.isoformat(),
            'is_pool': True,
        })
    
    # Add legacy recipients
    for recipient in legacy_recipients:
        progress = min((recipient.raised_amount / recipient.goal_amount) * 100, 100) if recipient.goal_amount > 0 else 0
        recipients_data.append({
            'id': recipient.id,
            'name': recipient.name,
            'category': recipient.category,
            'description': recipient.description,
            'wallet_address': recipient.wallet_address,
            'goal_amount': str(recipient.goal_amount),
            'raised_amount': str(recipient.raised_amount),
            'verification_proof': "Legacy Recipient",
            'image_url': "",
            'location': "",
            'urgency_level': 3,
            'progress_percentage': progress,
            'created_at': recipient.created_at.isoformat(),
            'is_pool': False,
        })
    
    return JsonResponse({'recipients': recipients_data})

@csrf_exempt
def record_donation(request):
    """Legacy endpoint - routes to appropriate new endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            recipient_id = data.get('recipient_id')
            
            # Check if it's a pool donation
            if isinstance(recipient_id, str) and recipient_id.startswith('pool_'):
                pool_id = int(recipient_id.replace('pool_', ''))
                data['pool_id'] = pool_id
                return donate_to_pool(request)
            else:
                # Legacy recipient donation
                return record_legacy_donation(request)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def record_legacy_donation(request):
    """Handle legacy recipient donations"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['donor_address', 'recipient_id', 'amount', 'tx_hash']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing field: {field}'}, status=400)
            
            # Check for duplicate transaction
            if Donation.objects.filter(tx_hash=data['tx_hash']).exists():
                return JsonResponse({'error': 'Donation already recorded'}, status=400)
            
            # Get recipient
            try:
                recipient = Recipient.objects.get(id=data['recipient_id'])
            except Recipient.DoesNotExist:
                return JsonResponse({'error': 'Recipient not found'}, status=404)
            
            # Create donation record
            donation_amount = Decimal(data['amount'])
            points_earned = calculate_points_and_tokens(donation_amount)
            
            donation = Donation.objects.create(
                donor_address=data['donor_address'].lower(),
                recipient=recipient,
                amount=donation_amount,
                tx_hash=data['tx_hash'],
                block_number=data.get('block_number'),
                points_earned=points_earned
            )
            
            # Update recipient raised amount
            recipient.raised_amount += donation_amount
            recipient.save()
            
            # Update user profile
            update_user_profile(data['donor_address'], donation_amount, points_earned, is_donor=True)
            
            # Create token reward
            create_token_reward(data['donor_address'], points_earned, 'legacy_donation', data['tx_hash'])
            
            return JsonResponse({
                'success': True,
                'donation_id': donation.id,
                'points_earned': points_earned,
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# HELPER FUNCTIONS

def calculate_points_and_tokens(amount_eth, donation_type='standard', cause_type='standard'):
    """Updated calculation using new tokenomics"""
    # Convert to USD (assuming $2500 per ETH)
    usd_amount = float(amount_eth) * 2500
    
    # Base rates
    base_tokens = usd_amount * 100  # 100 $UMAN per $1
    base_points = usd_amount * 1000  # 1000 points per $1
    
    # Apply multipliers
    if donation_type == 'p2p':
        base_tokens *= 1.2  # 20% P2P bonus
        base_points *= 1.2
    
    if cause_type == 'emergency':
        base_tokens *= 2.5  # Emergency 2.5x
        base_points *= 2.5
    
    return max(int(base_points), 1), max(int(base_tokens), 1)

def update_user_profile(wallet_address, donated_amount, points_earned, is_donor=True, received_amount=None):
    """Update or create user profile"""
    wallet_address = wallet_address.lower()
    
    profile, created = UserProfile.objects.get_or_create(
        wallet_address=wallet_address,
        defaults={
            'total_donated': donated_amount if is_donor else Decimal('0'),
            'total_received': received_amount or Decimal('0'),
            'total_points': points_earned,
            'donation_count': 1 if is_donor else 0,
            'first_donation_date': datetime.now() if is_donor else None,
            'last_donation_date': datetime.now() if is_donor else None,
        }
    )
    
    if not created:
        if is_donor:
            profile.total_donated += donated_amount
            profile.total_points += points_earned
            profile.donation_count += 1
            profile.last_donation_date = datetime.now()
            
            if not profile.first_donation_date:
                profile.first_donation_date = datetime.now()
        
        if received_amount:
            profile.total_received += received_amount
        
        profile.save()
    
    return profile

def create_token_reward(wallet_address, points_earned, reason, tx_hash):
    """Create token reward for future airdrop"""
    try:
        profile = UserProfile.objects.get(wallet_address=wallet_address.lower())
        
        # Calculate token amount (1 point = 0.1 tokens)
        token_amount = Decimal(points_earned) * Decimal('0.1')
        
        # Apply multipliers
        multiplier = Decimal('1.0')
        if reason == 'social_donation_frame':
            multiplier = Decimal('1.2')  # 20% bonus for frame interactions
        elif reason == 'early_adopter':
            multiplier = Decimal('2.0')  # 100% bonus for early adopters
        
        final_amount = token_amount * multiplier
        
        TokenReward.objects.create(
            user=profile,
            amount=final_amount,
            reason=reason,
            multiplier=multiplier,
            related_donation_tx=tx_hash,
            frame_interaction=(reason == 'social_donation_frame')
        )
        
        # Update user's total tokens earned
        profile.tokens_earned += final_amount
        profile.save()
        
    except UserProfile.DoesNotExist:
        pass  # Profile will be created on next donation

def get_user_stats(wallet_address):
    """Get comprehensive user stats"""
    wallet_address = wallet_address.lower()
    
    try:
        profile = UserProfile.objects.get(wallet_address=wallet_address)
        rank = get_user_rank(wallet_address)
        
        return {
            'total_donated': str(profile.total_donated),
            'total_received': str(profile.total_received),
            'total_points': profile.total_points,
            'donation_count': profile.donation_count,
            'tokens_earned': str(profile.tokens_earned),
            'rank': rank,
            'first_donation': profile.first_donation_date.isoformat() if profile.first_donation_date else None,
            'last_donation': profile.last_donation_date.isoformat() if profile.last_donation_date else None,
        }
    except UserProfile.DoesNotExist:
        return {
            'total_donated': '0',
            'total_received': '0',
            'total_points': 0,
            'donation_count': 0,
            'tokens_earned': '0',
            'rank': None,
            'first_donation': None,
            'last_donation': None,
        }

def get_user_rank(user_address):
    """Get user's current rank"""
    try:
        user_profile = UserProfile.objects.get(wallet_address=user_address.lower())
        higher_ranked = UserProfile.objects.filter(
            is_public_profile=True,
            total_points__gt=user_profile.total_points
        ).count()
        return higher_ranked + 1
    except UserProfile.DoesNotExist:
        return None

def get_time_ago(timestamp):
    """Convert timestamp to human-readable time ago"""
    from django.utils import timezone
    now = timezone.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600}h ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60}m ago"
    else:
        return "just now"

# TOKEN AND AIRDROP ENDPOINTS

def token_rewards(request):
    """Get user's token rewards for airdrop"""
    wallet_address = request.GET.get('address', '').lower()
    
    if not wallet_address:
        return JsonResponse({'error': 'Address required'}, status=400)
    
    try:
        profile = UserProfile.objects.get(wallet_address=wallet_address)
        rewards = TokenReward.objects.filter(user=profile).order_by('-created_at')
        
        rewards_data = []
        for reward in rewards:
            rewards_data.append({
                'id': reward.id,
                'amount': str(reward.amount),
                'reason': reward.reason,
                'multiplier': str(reward.multiplier),
                'is_claimed': reward.is_claimed,
                'frame_interaction': reward.frame_interaction,
                'created_at': reward.created_at.isoformat(),
            })
        
        return JsonResponse({
            'total_earned': str(profile.tokens_earned),
            'total_claimed': str(profile.tokens_claimed),
            'pending_claim': str(profile.tokens_earned - profile.tokens_claimed),
            'rewards': rewards_data
        })
        
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'total_earned': '0',
            'total_claimed': '0',
            'pending_claim': '0',
            'rewards': []
        })

def airdrop_eligibility(request):
    """Check airdrop eligibility"""
    wallet_address = request.GET.get('address', '').lower()
    min_points = int(request.GET.get('min_points', 100))
    
    if not wallet_address:
        return JsonResponse({'error': 'Address required'}, status=400)
    
    try:
        profile = UserProfile.objects.get(wallet_address=wallet_address)
        
        is_eligible = profile.total_points >= min_points
        multiplier = Decimal('1.0')
        
        # Early adopter bonus
        if profile.first_donation_date and profile.first_donation_date < datetime.now() - timedelta(days=30):
            multiplier = Decimal('2.0')
        
        # Active user bonus
        if profile.donation_count >= 10:
            multiplier = max(multiplier, Decimal('1.5'))
        
        # Frame interaction bonus
        frame_donations = TokenReward.objects.filter(
            user=profile,
            frame_interaction=True
        ).count()
        
        if frame_donations >= 5:
            multiplier = max(multiplier, Decimal('1.2'))
        
        final_tokens = profile.tokens_earned * multiplier
        
        return JsonResponse({
            'eligible': is_eligible,
            'total_points': profile.total_points,
            'base_tokens': str(profile.tokens_earned),
            'multiplier': str(multiplier),
            'final_tokens': str(final_tokens),
            'reason': get_multiplier_reason(profile, frame_donations),
            'rank': get_user_rank(wallet_address),
        })
        
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'eligible': False,
            'total_points': 0,
            'base_tokens': '0',
            'multiplier': '1.0',
            'final_tokens': '0',
            'reason': 'No donation history',
            'rank': None,
        })

def get_multiplier_reason(profile, frame_donations):
    """Get reason for token multiplier"""
    reasons = []
    
    if profile.first_donation_date and profile.first_donation_date < datetime.now() - timedelta(days=30):
        reasons.append("Early Adopter (2x)")
    
    if profile.donation_count >= 10:
        reasons.append("Active Donor (1.5x)")
    
    if frame_donations >= 5:
        reasons.append("Frame User (1.2x)")
    
    return " + ".join(reasons) if reasons else "Base multiplier"


# Add these new endpoints to your existing views.py

# FARCASTER MINI APP SPECIFIC ENDPOINTS

def farcaster_recipients(request):
    """API endpoint specifically for Farcaster mini app - simplified data"""
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    category = request.GET.get('category', 'all')
    
    # Get pools and legacy recipients
    pools = DonationPool.objects.filter(is_active=True)
    legacy_recipients = Recipient.objects.filter(is_verified=True, is_active=True)
    
    all_recipients = []
    
    # Add pools as recipients (simplified for mini app)
    for pool in pools:
        if category == 'all' or pool.pool_type == category:
            all_recipients.append({
                'id': pool.id,
                'name': pool.name,
                'category': pool.pool_type,
                'description': pool.description,
                'goal_amount': 10000,  # Pools have ongoing goals
                'raised_amount': float(pool.total_raised),
                'donor_count': pool.donor_count,
                'urgency_level': 3,
                'location': 'Global',
                'wallet_address': pool.wallet_address,
                'created_at': pool.created_at.isoformat(),
            })
    
    # Add legacy recipients
    for recipient in legacy_recipients:
        if category == 'all' or recipient.category == category:
            all_recipients.append({
                'id': recipient.id,
                'name': recipient.name,
                'category': recipient.category,
                'description': recipient.description,
                'goal_amount': float(recipient.goal_amount),
                'raised_amount': float(recipient.raised_amount),
                'donor_count': recipient.donations.count(),
                'urgency_level': 4,  # Legacy recipients are more urgent
                'location': 'Various',
                'wallet_address': recipient.wallet_address,
                'created_at': recipient.created_at.isoformat(),
            })
    
    # Paginate
    paginator = Paginator(all_recipients, limit)
    try:
        recipients_page = paginator.page(page)
    except:
        recipients_page = paginator.page(1)
    
    return JsonResponse({
        'recipients': list(recipients_page),
        'pagination': {
            'current_page': recipients_page.number,
            'total_pages': paginator.num_pages,
            'has_next': recipients_page.has_next(),
        }
    })

def farcaster_stats(request):
    """Simplified stats for Farcaster mini app"""
    # Calculate totals
    pool_raised = DonationPool.objects.aggregate(Sum('total_raised'))['total_raised__sum'] or 0
    legacy_raised = Recipient.objects.aggregate(Sum('raised_amount'))['raised_amount__sum'] or 0
    
    pool_goals = DonationPool.objects.count() * 10000  # Assume 10k goal per pool
    legacy_goals = Recipient.objects.aggregate(Sum('goal_amount'))['goal_amount__sum'] or 0
    
    total_donors = UserProfile.objects.filter(total_donated__gt=0).count()
    active_recipients = DonationPool.objects.filter(is_active=True).count() + Recipient.objects.filter(is_active=True).count()
    
    return JsonResponse({
        'total_needed': int(pool_goals + float(legacy_goals)),
        'total_raised': int(pool_raised + float(legacy_raised)),
        'active_recipients': active_recipients,
        'total_donors': total_donors,
    })

@csrf_exempt
def record_farcaster_donation(request):
    """Record donation from Farcaster mini app"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['donor_address', 'recipient_id', 'amount_usd', 'amount_eth', 'tx_hash']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing field: {field}'}, status=400)
            
            # Check for duplicate transaction
            if (PoolDonation.objects.filter(tx_hash=data['tx_hash']).exists() or
                Donation.objects.filter(tx_hash=data['tx_hash']).exists()):
                return JsonResponse({'error': 'Donation already recorded'}, status=400)
            
            recipient_id = data['recipient_id']
            donor_address = data['donor_address'].lower()
            amount_eth = Decimal(str(data['amount_eth']))
            amount_usd = data['amount_usd']
            
            # Try to find as pool first
            try:
                pool = DonationPool.objects.get(id=recipient_id)
                
                # Create pool donation
                donation = PoolDonation.objects.create(
                    donor_address=donor_address,
                    pool=pool,
                    amount=amount_eth,
                    tx_hash=data['tx_hash'],
                    block_number=data.get('block_number'),
                    points_earned=calculate_points_and_tokens(amount_eth)
                )
                
                # Update pool stats
                pool.total_raised += amount_eth
                pool.donor_count = pool.donations.values('donor_address').distinct().count()
                pool.save()
                
                recipient_type = 'pool'
                
            except DonationPool.DoesNotExist:
                # Try legacy recipient
                try:
                    recipient = Recipient.objects.get(id=recipient_id)
                    
                    # Create legacy donation
                    donation = Donation.objects.create(
                        donor_address=donor_address,
                        recipient=recipient,
                        amount=amount_eth,
                        tx_hash=data['tx_hash'],
                        block_number=data.get('block_number'),
                        points_earned=calculate_points_and_tokens(amount_eth)
                    )
                    
                    # Update recipient raised amount
                    recipient.raised_amount += amount_eth
                    recipient.save()
                    
                    recipient_type = 'legacy'
                    
                except Recipient.DoesNotExist:
                    return JsonResponse({'error': 'Recipient not found'}, status=404)
            
            # Update user profile
            points_earned = calculate_points_and_tokens(amount_eth)
            update_user_profile(donor_address, amount_eth, points_earned, is_donor=True)
            
            # Create token reward
            create_token_reward(donor_address, points_earned, f'{recipient_type}_donation', data['tx_hash'])
            
            return JsonResponse({
                'success': True,
                'donation_id': donation.id,
                'points_earned': points_earned,
                'recipient_type': recipient_type,
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def landing_stats(request):
    """Get real-time stats for landing page"""
    # Calculate total donated from all sources
    total_donated_pools = PoolDonation.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    total_donated_social = SocialDonation.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    total_donated_legacy = Donation.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
    total_donated = total_donated_pools + total_donated_social + total_donated_legacy
    
    # Get active donors count
    active_donors = UserProfile.objects.filter(total_donated__gt=0).count()
    
    # Get active pools count
    active_pools = DonationPool.objects.filter(is_active=True).count()
    
    # Calculate tokens distributed per 1 ETH (current epoch multiplier)
    tokens_per_eth = 5000000  # 5M tokens for Epoch 0
    
    return JsonResponse({
        'total_donated': str(total_donated),
        'active_donors': active_donors,
        'active_pools': active_pools,
        'tokens_per_eth': f"{tokens_per_eth:,}+"
    })

def pools_landing_data(request):
    """Get pools data for landing page display"""
    pools = DonationPool.objects.filter(is_active=True).order_by('pool_type')
    
    pools_data = []
    for pool in pools:
        # Calculate progress percentage (assuming pools have ongoing goals)
        goal_amount = 10.0  # 10 ETH goal per pool, adjust as needed
        progress = min((float(pool.total_raised) / goal_amount) * 100, 100) if goal_amount > 0 else 0
        
        pools_data.append({
            'id': pool.id,
            'name': pool.name,
            'pool_type': pool.pool_type,
            'description': pool.description,
            'emoji': pool.emoji,
            'total_raised': str(pool.total_raised),
            'donor_count': pool.donor_count,
            'allocation_percentage': str(pool.allocation_percentage),
            'progress_percentage': round(progress, 1),
        })
    
    return JsonResponse({'pools': pools_data})