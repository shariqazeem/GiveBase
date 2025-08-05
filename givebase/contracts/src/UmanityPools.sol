// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";

interface IUmanityToken {
    function mint(address to, uint256 amount) external;
}

// Soulbound Impact Points NFT
contract ImpactPointsNFT is ERC721, ERC721Enumerable, Ownable {
    struct ImpactProfile {
        uint256 totalPoints;
        uint256 totalDonated; // in USD cents
        uint256 donationCount;
        uint256 emergencyDonations;
        uint256 verifiedCauseDonations;
        uint256 p2pDonations;
        uint256 firstDonationTime;
        uint256 lastDonationTime;
        string displayName;
    }
    
    mapping(uint256 => ImpactProfile) public impactProfiles;
    mapping(address => uint256) public addressToTokenId;
    uint256 private _nextTokenId = 1;
    
    constructor() ERC721("Umanity Impact Points", "UIP") {}
    
    // Mint soulbound NFT for new donor
    function mintImpactNFT(address to) external onlyOwner returns (uint256) {
        require(addressToTokenId[to] == 0, "Already has Impact NFT");
        
        uint256 tokenId = _nextTokenId++;
        _safeMint(to, tokenId);
        addressToTokenId[to] = tokenId;
        
        impactProfiles[tokenId].firstDonationTime = block.timestamp;
        return tokenId;
    }
    
    // Update impact profile
    function updateImpactProfile(
        address user,
        uint256 pointsToAdd,
        uint256 usdAmountCents,
        string memory donationType
    ) external onlyOwner {
        uint256 tokenId = addressToTokenId[user];
        require(tokenId != 0, "No Impact NFT found");
        
        ImpactProfile storage profile = impactProfiles[tokenId];
        profile.totalPoints += pointsToAdd;
        profile.totalDonated += usdAmountCents;
        profile.donationCount++;
        profile.lastDonationTime = block.timestamp;
        
        // Track donation types
        if (keccak256(bytes(donationType)) == keccak256(bytes("emergency"))) {
            profile.emergencyDonations++;
        } else if (keccak256(bytes(donationType)) == keccak256(bytes("verified"))) {
            profile.verifiedCauseDonations++;
        } else if (keccak256(bytes(donationType)) == keccak256(bytes("p2p"))) {
            profile.p2pDonations++;
        }
    }
    
    // Soulbound: Override transfers to make non-transferable
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 tokenId,
        uint256 batchSize
    ) internal override(ERC721, ERC721Enumerable) {
        require(from == address(0) || to == address(0), "Soulbound: Transfer not allowed");
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
    }
    
    function supportsInterface(bytes4 interfaceId)
        public view override(ERC721, ERC721Enumerable) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
    
    // Get user's impact profile
    function getImpactProfile(address user) external view returns (ImpactProfile memory) {
        uint256 tokenId = addressToTokenId[user];
        require(tokenId != 0, "No Impact NFT found");
        return impactProfiles[tokenId];
    }
}

contract UmanityPools is Ownable, ReentrancyGuard {
    // Pool structure
    struct Pool {
        string name;
        string description;
        string emoji;
        uint256 balance;
        uint256 donorCount;
        uint256 allocationPercentage;
        bool isActive;
        bool isVerified; // For bonus calculations
        bool isEmergency; // For emergency bonus
    }
    
    // State variables
    mapping(uint256 => Pool) public pools;
    mapping(address => mapping(uint256 => uint256)) public userPoolDonations;
    
    uint256 public totalPools;
    uint256 public totalDonated; // in Wei
    uint256 public totalDonors;
    
    // USD Price Oracle (simplified - in production use Chainlink)
    uint256 public ethToUsdRate = 2500; // $2500 per ETH (update manually or via oracle)
    
    // Token and NFT contracts
    IUmanityToken public umanityToken;
    ImpactPointsNFT public impactPointsNFT;
    
    // Reward rates (base: 100 UMAN per $1 USD)
    uint256 public constant BASE_REWARD_RATE = 100 * 10**18; // 100 UMAN tokens
    uint256 public constant VERIFIED_BONUS = 50; // +50% bonus
    uint256 public constant EMERGENCY_BONUS = 150; // +150% bonus
    uint256 public constant P2P_PUBLIC_BONUS = 32; // +32% bonus
    
    // Events
    event PoolCreated(uint256 indexed poolId, string name, bool isVerified, bool isEmergency);
    event DonationMade(
        address indexed donor, 
        uint256 indexed poolId, 
        uint256 ethAmount, 
        uint256 usdAmount, 
        uint256 tokensEarned,
        uint256 pointsEarned
    );
    event EthPriceUpdated(uint256 newPrice);
    
    constructor() {
    // Deploy Impact Points NFT
    impactPointsNFT = new ImpactPointsNFT();
    
    // Initialize pools with new bonus structure
    _createPool("Emergency Fund", "Help those in urgent need worldwide", unicode"🚨", 25, true, true, true);

    _createPool("Community Projects", "Fund community initiatives", unicode"🏘️", 30, true, true, false); // Verified only
    _createPool("Creator Support", "Support content creators", unicode"🎨", 20, true, false, false); // Base rate
    _createPool("Platform Development", "Improve Umanity platform", unicode"⚡", 25, true, false, false); // Base rate
}

    
    // Set token contract address (called after token deployment)
    function setTokenContract(address _tokenAddress) external onlyOwner {
        umanityToken = IUmanityToken(_tokenAddress);
    }
    
    // Update ETH/USD price (in production, use Chainlink oracle)
    function updateEthPrice(uint256 _newPrice) external onlyOwner {
        ethToUsdRate = _newPrice;
        emit EthPriceUpdated(_newPrice);
    }
    
    // Create a new pool
    function _createPool(
        string memory _name,
        string memory _description,
        string memory _emoji,
        uint256 _allocationPercentage,
        bool _isActive,
        bool _isVerified,
        bool _isEmergency
    ) internal {
        pools[totalPools] = Pool({
            name: _name,
            description: _description,
            emoji: _emoji,
            balance: 0,
            donorCount: 0,
            allocationPercentage: _allocationPercentage,
            isActive: _isActive,
            isVerified: _isVerified,
            isEmergency: _isEmergency
        });
        
        emit PoolCreated(totalPools, _name, _isVerified, _isEmergency);
        totalPools++;
    }
    
    // Calculate USD amount from ETH
    function calculateUsdAmount(uint256 ethAmount) public view returns (uint256) {
        // Returns USD amount in cents (to avoid decimals)
        return (ethAmount * ethToUsdRate) / 10**16; // Convert from wei to cents
    }
    
    // Calculate token rewards based on USD amount and pool type
    function calculateTokenReward(uint256 usdCents, uint256 poolId) public view returns (uint256) {
        Pool memory pool = pools[poolId];
        uint256 usdDollars = usdCents / 100; // Convert cents to dollars
        uint256 baseReward = usdDollars * BASE_REWARD_RATE; // 100 UMAN per $1
        
        uint256 totalBonus = 0;
        
        if (pool.isEmergency) {
            totalBonus += EMERGENCY_BONUS; // +150%
        } else if (pool.isVerified) {
            totalBonus += VERIFIED_BONUS; // +50%
        }
        
        // Apply bonus
        uint256 bonusReward = (baseReward * totalBonus) / 100;
        return baseReward + bonusReward;
    }
    
    // Donate to a specific pool
    function donateToPool(uint256 _poolId) external payable nonReentrant {
        require(_poolId < totalPools, "Pool does not exist");
        require(pools[_poolId].isActive, "Pool is not active");
        require(msg.value > 0, "Donation must be greater than 0");
        
        Pool storage pool = pools[_poolId];
        
        // Calculate USD amount
        uint256 usdAmountCents = calculateUsdAmount(msg.value);
        uint256 tokenReward = calculateTokenReward(usdAmountCents, _poolId);
        
        // Calculate impact points (1 point per cent donated)
        uint256 impactPoints = usdAmountCents;
        
        // Update pool stats
        pool.balance += msg.value;
        
        // Track unique donors
        if (userPoolDonations[msg.sender][_poolId] == 0) {
            pool.donorCount++;
        }
        
        // Create or update Impact NFT
        if (impactPointsNFT.addressToTokenId(msg.sender) == 0) {
            impactPointsNFT.mintImpactNFT(msg.sender);
            totalDonors++;
        }
        
        // Update impact profile
        string memory donationType = pool.isEmergency ? "emergency" : 
                                   pool.isVerified ? "verified" : "regular";
        
        impactPointsNFT.updateImpactProfile(
            msg.sender, 
            impactPoints, 
            usdAmountCents, 
            donationType
        );
        
        userPoolDonations[msg.sender][_poolId] += msg.value;
        totalDonated += msg.value;
        
        // Mint token rewards
        if (address(umanityToken) != address(0)) {
            umanityToken.mint(msg.sender, tokenReward);
        }
        
        emit DonationMade(
            msg.sender, 
            _poolId, 
            msg.value, 
            usdAmountCents, 
            tokenReward, 
            impactPoints
        );
    }
    
    // Get pool information with reward preview
    function getPoolWithRewards(uint256 _poolId) external view returns (
        Pool memory pool,
        uint256 rewardsPer1USD,
        string memory bonusType
    ) {
        require(_poolId < totalPools, "Pool does not exist");
        pool = pools[_poolId];
        
        rewardsPer1USD = calculateTokenReward(100, _poolId) / 10**18; // Reward per $1 USD
        
        if (pool.isEmergency) {
            bonusType = "Emergency (+150% bonus)";
        } else if (pool.isVerified) {
            bonusType = "Verified (+50% bonus)";
        } else {
            bonusType = "Base rate";
        }
    }
    
    // Get user's impact statistics
    function getUserImpactStats(address user) external view returns (
        bool hasImpactNFT,
        uint256 totalPoints,
        uint256 totalDonatedUSD,
        uint256 donationCount,
        uint256 nftTokenId
    ) {
        nftTokenId = impactPointsNFT.addressToTokenId(user);
        hasImpactNFT = nftTokenId != 0;
        
        if (hasImpactNFT) {
            ImpactPointsNFT.ImpactProfile memory profile = impactPointsNFT.getImpactProfile(user);
            totalPoints = profile.totalPoints;
            totalDonatedUSD = profile.totalDonated / 100; // Convert cents to dollars
            donationCount = profile.donationCount;
        }
    }
    
    // Get platform statistics
    function getPlatformStats() external view returns (
        uint256 _totalDonatedETH,
        uint256 _totalDonatedUSD,
        uint256 _totalDonors,
        uint256 _totalPools,
        uint256 _activePools
    ) {
        uint256 activePools = 0;
        for (uint256 i = 0; i < totalPools; i++) {
            if (pools[i].isActive) {
                activePools++;
            }
        }
        
        return (
            totalDonated,
            calculateUsdAmount(totalDonated) / 100, // Convert to dollars
            totalDonors,
            totalPools,
            activePools
        );
    }
    
    // Withdraw funds from a pool (only owner)
    function withdrawPoolFunds(uint256 _poolId, address payable _to, uint256 _amount) 
        external onlyOwner nonReentrant {
        require(_poolId < totalPools, "Pool does not exist");
        require(_amount <= pools[_poolId].balance, "Insufficient pool balance");
        require(_to != address(0), "Invalid recipient address");
        
        pools[_poolId].balance -= _amount;
        _to.transfer(_amount);
    }
    
    // Emergency withdraw (only owner)
    function emergencyWithdraw() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
}