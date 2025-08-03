// import './style.css'
// import { sdk } from 'https://esm.sh/@farcaster/miniapp-sdk'

// // Create the main app HTML structure
// document.getElementById('app').innerHTML = `
//     <!-- Splash Screen (shown until SDK ready) -->
//     <div id="splashScreen" class="splash-screen">
//         <div class="logo text-4xl mb-4">GiveBase</div>
//         <div class="loading-spinner"></div>
//         <p class="text-gray-600 mt-4">Loading...</p>
//     </div>

//     <!-- Main App Content -->
//     <div id="mainContent" class="hidden bg-white text-gray-900 geometric-bg min-h-screen">
//         <!-- Header -->
//         <header class="nav-blur sticky top-0 z-50">
//             <div class="max-w-4xl mx-auto px-4 py-4">
//                 <div class="flex justify-between items-center">
//                     <div class="flex items-center space-x-3">
//                         <div class="logo">GiveBase</div>
//                         <span class="text-sm text-gray-600 font-medium">Help People in Need</span>
//                     </div>
//                     <div class="flex items-center space-x-3">
//                         <div id="networkInfo" class="hidden md:flex items-center space-x-2 px-3 py-2 bg-black/5 rounded-xl border border-black/10">
//                             <div class="w-2 h-2 bg-black rounded-full"></div>
//                             <span class="text-xs font-medium">Base</span>
//                         </div>
//                         <button id="connectWallet" class="primary-button px-4 py-2 rounded-xl text-white font-semibold text-sm">
//                             Connect Wallet
//                         </button>
//                     </div>
//                 </div>
//             </div>
//         </header>

//         <!-- Main Content -->
//         <main class="max-w-4xl mx-auto px-4 py-6">
//             <!-- Stats Summary -->
//             <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
//                 <div class="help-card rounded-2xl p-4 text-center">
//                     <div class="text-2xl font-black text-black" id="totalNeeded">$0</div>
//                     <div class="text-xs text-gray-500">Total Needed</div>
//                 </div>
//                 <div class="help-card rounded-2xl p-4 text-center">
//                     <div class="text-2xl font-black text-black" id="totalRaised">$0</div>
//                     <div class="text-xs text-gray-500">Funds Raised</div>
//                 </div>
//                 <div class="help-card rounded-2xl p-4 text-center">
//                     <div class="text-2xl font-black text-black" id="activeRecipients">0</div>
//                     <div class="text-xs text-gray-500">People Helped</div>
//                 </div>
//                 <div class="help-card rounded-2xl p-4 text-center">
//                     <div class="text-2xl font-black text-black" id="totalDonors">0</div>
//                     <div class="text-xs text-gray-500">Total Donors</div>
//                 </div>
//             </div>

//             <!-- Filter Options -->
//             <div class="flex flex-wrap gap-2 mb-6">
//                 <button onclick="filterRecipients('all')" class="filter-btn secondary-button px-4 py-2 rounded-xl text-sm font-medium" data-filter="all">
//                     All Cases
//                 </button>
//                 <button onclick="filterRecipients('medical')" class="filter-btn secondary-button px-4 py-2 rounded-xl text-sm font-medium" data-filter="medical">
//                     🏥 Medical
//                 </button>
//                 <button onclick="filterRecipients('emergency')" class="filter-btn secondary-button px-4 py-2 rounded-xl text-sm font-medium" data-filter="emergency">
//                     🚨 Emergency
//                 </button>
//                 <button onclick="filterRecipients('education')" class="filter-btn secondary-button px-4 py-2 rounded-xl text-sm font-medium" data-filter="education">
//                     🎓 Education
//                 </button>
//                 <button onclick="filterRecipients('community')" class="filter-btn secondary-button px-4 py-2 rounded-xl text-sm font-medium" data-filter="community">
//                     🏘️ Community
//                 </button>
//             </div>

//             <!-- Recipients List -->
//             <div id="recipientsList" class="space-y-6">
//                 <!-- Loading state -->
//                 <div class="flex justify-center py-12">
//                     <div class="loading-spinner"></div>
//                 </div>
//             </div>

//             <!-- Load More -->
//             <div id="loadMoreContainer" class="text-center mt-8 hidden">
//                 <button onclick="loadMoreRecipients()" class="secondary-button px-8 py-3 rounded-xl font-medium">
//                     Load More People
//                 </button>
//             </div>

//             <!-- Footer -->
//             <footer class="text-center py-8 mt-12 border-t border-gray-200">
//                 <p class="text-sm text-gray-500">
//                     Powered by <span class="font-semibold text-black">GiveBase</span> • 
//                     <a href="/app" class="text-black hover:underline">Full App</a> • 
//                     Built for Farcaster Community
//                 </p>
//             </footer>
//         </main>
//     </div>

//     <!-- Donation Modal -->
//     <div id="donationModal" class="fixed inset-0 modal-backdrop hidden z-50 flex items-center justify-center p-4">
//         <div class="modal-content rounded-3xl max-w-lg w-full p-6">
//             <div class="flex justify-between items-center mb-6">
//                 <h3 class="text-2xl font-bold">Help Someone in Need</h3>
//                 <button onclick="closeDonationModal()" class="text-gray-400 hover:text-black">
//                     <i class="fas fa-times text-xl"></i>
//                 </button>
//             </div>
            
//             <!-- Selected Recipient Info -->
//             <div id="selectedRecipientInfo" class="mb-6">
//                 <!-- Will be populated when modal opens -->
//             </div>
            
//             <!-- Quick Amount Selection -->
//             <div class="mb-6">
//                 <label class="block text-sm font-medium text-gray-700 mb-3">Choose Amount</label>
//                 <div class="grid grid-cols-2 md:grid-cols-4 gap-3 quick-donate-grid mb-4">
//                     <button onclick="selectAmount(5)" class="quick-donate-btn py-3 rounded-xl font-medium" data-amount="5">
//                         $5
//                     </button>
//                     <button onclick="selectAmount(10)" class="quick-donate-btn py-3 rounded-xl font-medium" data-amount="10">
//                         $10
//                     </button>
//                     <button onclick="selectAmount(25)" class="quick-donate-btn py-3 rounded-xl font-medium" data-amount="25">
//                         $25
//                     </button>
//                     <button onclick="selectAmount(50)" class="quick-donate-btn py-3 rounded-xl font-medium" data-amount="50">
//                         $50
//                     </button>
//                 </div>
                
//                 <!-- Custom Amount -->
//                 <div>
//                     <label class="block text-sm text-gray-600 mb-2">Or enter custom amount (USD)</label>
//                     <input type="number" id="customAmount" placeholder="Enter amount" min="1" step="1"
//                            class="form-input w-full rounded-xl px-4 py-3 text-sm">
//                 </div>
//             </div>

//             <!-- Optional Message -->
//             <div class="mb-6">
//                 <label class="block text-sm font-medium text-gray-700 mb-2">Message (optional)</label>
//                 <input type="text" id="donationMessage" placeholder="Send words of encouragement..." maxlength="200"
//                        class="form-input w-full rounded-xl px-4 py-3 text-sm">
//             </div>

//             <!-- Estimated Cost -->
//             <div class="bg-black/5 rounded-xl p-4 mb-6">
//                 <div class="flex justify-between text-sm mb-2">
//                     <span>Donation Amount:</span>
//                     <span id="estimatedUSD">$0</span>
//                 </div>
//                 <div class="flex justify-between text-sm mb-2">
//                     <span>Estimated ETH:</span>
//                     <span id="estimatedETH">~0 ETH</span>
//                 </div>
//                 <div class="flex justify-between text-sm text-gray-500">
//                     <span>Network Fee:</span>
//                     <span>~$0.50 (Base)</span>
//                 </div>
//             </div>
            
//             <button onclick="processDonation()" class="primary-button w-full py-4 rounded-xl text-white font-bold">
//                 <span id="donateButtonText">Send Donation</span>
//             </button>
//         </div>
//     </div>

//     <!-- Success Modal -->
//     <div id="successModal" class="fixed inset-0 modal-backdrop hidden z-50 flex items-center justify-center p-4">
//         <div class="modal-content rounded-3xl max-w-lg w-full p-6 text-center">
//             <div class="w-20 h-20 bg-black/10 rounded-full flex items-center justify-center mx-auto mb-6">
//                 <i class="fas fa-heart text-3xl text-black"></i>
//             </div>
//             <h3 class="text-2xl font-bold mb-4">Thank You for Your Kindness!</h3>
//             <p class="text-gray-600 mb-6">Your donation has been sent successfully. You've made a real difference in someone's life.</p>
            
//             <div class="bg-black/5 rounded-2xl p-4 mb-6">
//                 <div class="text-sm text-gray-500 mb-2">Transaction Hash</div>
//                 <div id="txHash" class="font-mono text-xs break-all text-black font-medium"></div>
//             </div>

//             <div class="grid grid-cols-2 gap-4 mb-6">
//                 <div class="help-card rounded-xl p-4">
//                     <div class="text-xl font-black text-black">$<span id="donatedAmount">0</span></div>
//                     <div class="text-xs text-gray-500">You Donated</div>
//                 </div>
//                 <div class="help-card rounded-xl p-4">
//                     <div class="text-xl font-black text-black" id="recipientProgress">0%</div>
//                     <div class="text-xs text-gray-500">Goal Progress</div>
//                 </div>
//             </div>
            
//             <div class="flex gap-3">
//                 <button onclick="shareOnFarcaster()" class="secondary-button flex-1 py-3 rounded-xl font-medium">
//                     <i class="fas fa-share mr-2"></i>Share Good Deed
//                 </button>
//                 <button onclick="closeSuccessModal()" class="primary-button flex-1 py-3 rounded-xl text-white font-medium">
//                     Help Others
//                 </button>
//             </div>
//         </div>
//     </div>
// `

// // Global variables
// let userAccount;
// let selectedRecipient;
// let currentFilter = 'all';
// let currentPage = 1;
// let hasMoreRecipients = false;
// let ethPrice = 2500; // Default ETH price in USD
// let farcasterProvider;
// let isConnected = false;

// // API Configuration
// const API_BASE = import.meta.env.DEV ? 'http://localhost:8000' : '';

// // Initialize the app
// async function initializeApp() {
//     try {
//         console.log('Initializing Farcaster Mini App...');
        
//         // Load initial data first
//         await loadRecipients();
//         await loadStats();
//         await fetchETHPrice();
        
//         // Hide splash screen and show main content immediately
//         document.getElementById('splashScreen').classList.add('hidden');
//         document.getElementById('mainContent').classList.remove('hidden');
        
//         // Call ready to hide Farcaster splash screen
//         await sdk.actions.ready();
//         console.log('✅ Farcaster Mini App ready called!');
        
//         // Initialize wallet after ready
//         await initializeFarcasterWallet();
        
//     } catch (error) {
//         console.error('Error initializing app:', error);
//         // Still show the app even if SDK fails
//         document.getElementById('splashScreen').classList.add('hidden');
//         document.getElementById('mainContent').classList.remove('hidden');
        
//         // Call ready anyway to prevent infinite loading
//         try {
//             await sdk.actions.ready();
//         } catch (readyError) {
//             console.error('Error calling ready:', readyError);
//         }
//     }
// }

// // Initialize Farcaster wallet
// async function initializeFarcasterWallet() {
//     try {
//         // Get Farcaster's Ethereum provider
//         farcasterProvider = await sdk.wallet.getEthereumProvider();
//         console.log('✅ Farcaster wallet provider obtained');
        
//         // Check if already connected
//         const accounts = await farcasterProvider.request({ 
//             method: 'eth_accounts' 
//         });
        
//         if (accounts && accounts.length > 0) {
//             userAccount = accounts[0];
//             isConnected = true;
//             updateWalletUI();
//             console.log('✅ Wallet already connected:', userAccount);
//         } else {
//             console.log('👛 Wallet not connected yet');
//         }
        
//         // Listen for account changes
//         farcasterProvider.on('accountsChanged', (accounts) => {
//             console.log('Accounts changed:', accounts);
//             if (accounts.length > 0) {
//                 userAccount = accounts[0];
//                 isConnected = true;
//                 updateWalletUI();
//             } else {
//                 userAccount = null;
//                 isConnected = false;
//                 updateWalletUI();
//             }
//         });
        
//     } catch (error) {
//         console.error('Error initializing Farcaster wallet:', error);
//         // Update UI to show wallet not available
//         const connectBtn = document.getElementById('connectWallet');
//         connectBtn.textContent = 'Wallet Not Available';
//         connectBtn.disabled = true;
//     }
// }

// // Handle wallet connection using Farcaster's native wallet
// async function handleWalletConnect() {
//     if (!farcasterProvider) {
//         alert('Farcaster wallet not available. Please make sure you\'re using this in a Farcaster client.');
//         return;
//     }

//     if (isConnected && userAccount) {
//         // Already connected, show wallet info
//         alert(`Connected to: ${userAccount}`);
//         return;
//     }

//     try {
//         console.log('🔗 Requesting wallet connection...');
        
//         // Request account access from Farcaster wallet
//         const accounts = await farcasterProvider.request({
//             method: 'eth_requestAccounts'
//         });
        
//         if (accounts && accounts.length > 0) {
//             userAccount = accounts[0];
//             isConnected = true;
//             updateWalletUI();
//             console.log('✅ Wallet connected successfully:', userAccount);
//         } else {
//             console.error('No accounts returned');
//             alert('Failed to connect wallet. Please try again.');
//         }
        
//     } catch (error) {
//         console.error('Error connecting wallet:', error);
        
//         if (error.code === 4001) {
//             alert('Connection cancelled. Please approve the connection request.');
//         } else if (error.code === -32002) {
//             alert('Connection request pending. Please check your wallet.');
//         } else {
//             alert('Failed to connect wallet. Please try again.');
//         }
//     }
// }

// function updateWalletUI() {
//     const connectBtn = document.getElementById('connectWallet');
//     const networkInfo = document.getElementById('networkInfo');
    
//     if (isConnected && userAccount) {
//         const shortAddress = `${userAccount.substring(0, 6)}...${userAccount.substring(38)}`;
//         connectBtn.textContent = shortAddress;
//         connectBtn.classList.remove('primary-button');
//         connectBtn.classList.add('secondary-button');
//         networkInfo.classList.remove('hidden');
//     } else {
//         connectBtn.textContent = 'Connect Wallet';
//         connectBtn.classList.add('primary-button');
//         connectBtn.classList.remove('secondary-button');
//         networkInfo.classList.add('hidden');
//     }
// }

// // Load recipients from Django API
// async function loadRecipients(page = 1, filter = 'all') {
//     try {
//         let url = `${API_BASE}/api/farcaster-recipients/?page=${page}&limit=10`;
//         if (filter !== 'all') {
//             url += `&category=${filter}`;
//         }
        
//         const response = await fetch(url);
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
        
//         const data = await response.json();
        
//         const recipientsList = document.getElementById('recipientsList');
        
//         if (page === 1) {
//             recipientsList.innerHTML = '';
//         }
        
//         if (data.recipients.length === 0 && page === 1) {
//             recipientsList.innerHTML = `
//                 <div class="text-center py-12">
//                     <div class="text-6xl mb-4">💙</div>
//                     <h3 class="text-xl font-bold mb-2">No one needs help right now</h3>
//                     <p class="text-gray-600">Check back later or help us spread the word about GiveBase!</p>
//                 </div>
//             `;
//             return;
//         }
        
//         data.recipients.forEach(recipient => {
//             const progress = Math.min((parseFloat(recipient.raised_amount) / parseFloat(recipient.goal_amount)) * 100, 100);
//             const urgencyClass = getUrgencyClass(recipient.urgency_level || 3);
            
//             const card = document.createElement('div');
//             card.className = `help-card rounded-3xl p-6 recipient-card`;
//             card.setAttribute('data-category', recipient.category);
//             card.innerHTML = `
//                 <div class="flex flex-col md:flex-row gap-6">
//                     <!-- Profile Image -->
//                     <div class="flex-shrink-0">
//                         <div class="w-24 h-24 bg-gradient-to-r from-black to-gray-700 rounded-2xl flex items-center justify-center text-white text-2xl font-bold">
//                             ${recipient.name.charAt(0).toUpperCase()}
//                         </div>
//                         <div class="mt-2 text-center">
//                             <span class="${urgencyClass} text-white text-xs px-2 py-1 rounded-full font-medium">
//                                 ${getUrgencyText(recipient.urgency_level || 3)}
//                             </span>
//                         </div>
//                     </div>
                    
//                     <!-- Content -->
//                     <div class="flex-1">
//                         <div class="flex flex-col md:flex-row md:justify-between md:items-start mb-4">
//                             <div>
//                                 <h3 class="text-xl font-bold text-black mb-2">${recipient.name}</h3>
//                                 <div class="flex items-center space-x-2 mb-2">
//                                     <span class="px-3 py-1 bg-black/10 text-black rounded-full text-sm font-medium">
//                                         ${getCategoryIcon(recipient.category)} ${recipient.category}
//                                     </span>
//                                     ${recipient.location ? `<span class="text-sm text-gray-500">📍 ${recipient.location}</span>` : ''}
//                                 </div>
//                             </div>
//                             <div class="text-right mt-4 md:mt-0">
//                                 <div class="text-2xl font-black text-black">$${parseFloat(recipient.raised_amount).toLocaleString()}</div>
//                                 <div class="text-sm text-gray-500">of $${parseFloat(recipient.goal_amount).toLocaleString()}</div>
//                             </div>
//                         </div>
                        
//                         <p class="text-gray-700 mb-4 leading-relaxed">${recipient.description}</p>
                        
//                         <!-- Progress Bar -->
//                         <div class="mb-4">
//                             <div class="flex justify-between text-sm mb-2">
//                                 <span class="text-gray-600">${progress.toFixed(1)}% funded</span>
//                                 <span class="text-gray-600">${recipient.donor_count || 0} donors</span>
//                             </div>
//                             <div class="w-full bg-gray-200 rounded-full h-3">
//                                 <div class="progress-bar h-3 rounded-full" style="width: ${progress}%"></div>
//                             </div>
//                         </div>
                        
//                         <!-- Action Buttons -->
//                         <div class="flex gap-3">
//                             <button onclick="openDonationModal(${recipient.id})" class="primary-button flex-1 py-3 rounded-xl text-white font-bold">
//                                 <i class="fas fa-heart mr-2"></i>Donate Now
//                             </button>
//                             <button onclick="shareRecipient(${recipient.id})" class="secondary-button px-6 py-3 rounded-xl font-medium">
//                                 <i class="fas fa-share mr-2"></i>Share
//                             </button>
//                         </div>
//                     </div>
//                 </div>
//             `;
//             recipientsList.appendChild(card);
//         });
        
//         // Handle pagination
//         const loadMoreContainer = document.getElementById('loadMoreContainer');
//         if (data.pagination && data.pagination.has_next) {
//             loadMoreContainer.classList.remove('hidden');
//             hasMoreRecipients = true;
//             currentPage = page;
//         } else {
//             loadMoreContainer.classList.add('hidden');
//             hasMoreRecipients = false;
//         }
        
//     } catch (error) {
//         console.error('Error loading recipients:', error);
//         const recipientsList = document.getElementById('recipientsList');
//         recipientsList.innerHTML = `
//             <div class="text-center py-12">
//                 <div class="text-4xl mb-4">⚠️</div>
//                 <h3 class="text-xl font-bold mb-2">Unable to load recipients</h3>
//                 <p class="text-gray-600">Please check your connection and try again.</p>
//                 <button onclick="loadRecipients()" class="primary-button mt-4 px-6 py-2 rounded-xl text-white font-medium">
//                     Try Again
//                 </button>
//             </div>
//         `;
//     }
// }

// // Load platform stats from Django API
// async function loadStats() {
//     try {
//         const response = await fetch(`${API_BASE}/api/farcaster-stats/`);
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
        
//         const data = await response.json();
        
//         document.getElementById('totalNeeded').textContent = `${data.total_needed.toLocaleString()}`;
//         document.getElementById('totalRaised').textContent = `${data.total_raised.toLocaleString()}`;
//         document.getElementById('activeRecipients').textContent = data.active_recipients;
//         document.getElementById('totalDonors').textContent = data.total_donors;
        
//     } catch (error) {
//         console.error('Error loading stats:', error);
//         // Keep default values if API fails
//     }
// }

// // Fetch current ETH price
// async function fetchETHPrice() {
//     try {
//         const response = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd');
//         const data = await response.json();
//         ethPrice = data.ethereum.usd;
//     } catch (error) {
//         console.error('Error fetching ETH price:', error);
//         // Keep default price
//     }
// }

// // Filter recipients
// window.filterRecipients = function(category) {
//     currentFilter = category;
//     currentPage = 1;
    
//     // Update filter buttons
//     document.querySelectorAll('.filter-btn').forEach(btn => {
//         btn.classList.remove('primary-button');
//         btn.classList.add('secondary-button');
//     });
    
//     const activeBtn = document.querySelector(`[data-filter="${category}"]`);
//     if (activeBtn) {
//         activeBtn.classList.remove('secondary-button');
//         activeBtn.classList.add('primary-button');
//     }
    
//     loadRecipients(1, category);
// }

// // Donation modal functions  
// window.openDonationModal = function(recipientId) {
//     if (!isConnected || !userAccount) {
//         alert('Please connect your Farcaster wallet first!');
//         return;
//     }
    
//     // Fetch recipient data from Django API
//     fetch(`${API_BASE}/api/farcaster-recipients/?page=1&limit=100`)
//         .then(res => res.json())
//         .then(data => {
//             const recipient = data.recipients.find(r => r.id === recipientId);
//             if (!recipient) {
//                 alert('Recipient not found');
//                 return;
//             }
            
//             selectedRecipient = recipient;
            
//             // Populate modal
//             document.getElementById('selectedRecipientInfo').innerHTML = `
//                 <div class="help-card rounded-2xl p-4">
//                     <div class="flex items-center space-x-4 mb-3">
//                         <div class="w-12 h-12 bg-gradient-to-r from-black to-gray-700 rounded-xl flex items-center justify-center text-white font-bold">
//                             ${recipient.name.charAt(0).toUpperCase()}
//                         </div>
//                         <div>
//                             <h4 class="font-bold text-lg text-black">${recipient.name}</h4>
//                             <span class="px-2 py-1 bg-black/10 text-black rounded-full text-xs font-medium">
//                                 ${getCategoryIcon(recipient.category)} ${recipient.category}
//                             </span>
//                         </div>
//                     </div>
//                     <p class="text-sm text-gray-700">${recipient.description.substring(0, 150)}...</p>
//                     <div class="mt-3 text-sm">
//                         <span class="text-gray-600">Goal: ${parseFloat(recipient.goal_amount).toLocaleString()}</span>
//                         <span class="mx-2">•</span>
//                         <span class="text-gray-600">Raised: ${parseFloat(recipient.raised_amount).toLocaleString()}</span>
//                     </div>
//                 </div>
//             `;
            
//             document.getElementById('donationModal').classList.remove('hidden');
//         })
//         .catch(error => {
//             console.error('Error loading recipient:', error);
//             alert('Unable to load recipient details. Please try again.');
//         });
// }

// window.closeDonationModal = function() {
//     document.getElementById('donationModal').classList.add('hidden');
//     selectedRecipient = null;
    
//     // Reset form
//     document.querySelectorAll('.quick-donate-btn').forEach(btn => {
//         btn.classList.remove('selected');
//     });
//     document.getElementById('customAmount').value = '';
//     document.getElementById('donationMessage').value = '';
//     updateEstimatedCosts();
// }

// window.selectAmount = function(amount) {
//     // Update buttons
//     document.querySelectorAll('.quick-donate-btn').forEach(btn => {
//         btn.classList.remove('selected');
//     });
    
//     const selectedBtn = document.querySelector(`[data-amount="${amount}"]`);
//     if (selectedBtn) {
//         selectedBtn.classList.add('selected');
//     }
    
//     // Clear custom amount
//     document.getElementById('customAmount').value = '';
    
//     // Update estimates
//     updateEstimatedCosts(amount);
// }

// function updateEstimatedCosts(presetAmount = null) {
//     let amount = presetAmount;
    
//     if (!amount) {
//         // Check if custom amount is entered
//         const customAmount = parseFloat(document.getElementById('customAmount').value) || 0;
        
//         // Check if any preset button is selected
//         const selectedBtn = document.querySelector('.quick-donate-btn.selected');
//         const presetAmount = selectedBtn ? parseFloat(selectedBtn.getAttribute('data-amount')) : 0;
        
//         amount = Math.max(customAmount, presetAmount);
//     }
    
//     const ethAmount = amount / ethPrice;
    
//     document.getElementById('estimatedUSD').textContent = `${amount.toFixed(2)}`;
//     document.getElementById('estimatedETH').textContent = `~${ethAmount.toFixed(6)} ETH`;
// }

// // Process donation using Farcaster wallet and Django API
// window.processDonation = async function() {
//     if (!isConnected || !userAccount || !farcasterProvider) {
//         alert('Please connect your Farcaster wallet first!');
//         return;
//     }
    
//     if (!selectedRecipient) {
//         alert('No recipient selected!');
//         return;
//     }
    
//     // Get donation amount
//     const customAmount = parseFloat(document.getElementById('customAmount').value) || 0;
//     const selectedBtn = document.querySelector('.quick-donate-btn.selected');
//     const presetAmount = selectedBtn ? parseFloat(selectedBtn.getAttribute('data-amount')) : 0;
//     const usdAmount = Math.max(customAmount, presetAmount);
    
//     if (usdAmount < 1) {
//         alert('Minimum donation is $1');
//         return;
//     }
    
//     const ethAmount = usdAmount / ethPrice;
//     const message = document.getElementById('donationMessage').value.trim();
    
//     const donateBtn = document.getElementById('donateButtonText');
//     donateBtn.textContent = 'Processing...';
    
//     try {
//         // Convert ETH amount to Wei (hex string)
//         const weiAmount = '0x' + Math.floor(ethAmount * 1e18).toString(16);
        
//         console.log('Sending transaction:', {
//             to: selectedRecipient.wallet_address,
//             value: weiAmount,
//             from: userAccount
//         });
        
//         // Send transaction using Farcaster provider
//         const txHash = await farcasterProvider.request({
//             method: 'eth_sendTransaction',
//             params: [{
//                 from: userAccount,
//                 to: selectedRecipient.wallet_address,
//                 value: weiAmount,
//                 gas: '0x5208', // 21000 in hex
//             }]
//         });
        
//         console.log('✅ Transaction sent successfully:', txHash);
        
//         // Record donation in Django backend
//         try {
//             const response = await fetch(`${API_BASE}/api/record-farcaster-donation/`, {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                 },
//                 body: JSON.stringify({
//                     donor_address: userAccount,
//                     recipient_id: selectedRecipient.id,
//                     amount_usd: usdAmount,
//                     amount_eth: ethAmount,
//                     message: message,
//                     tx_hash: txHash,
//                     platform: 'farcaster'
//                 }),
//             });
            
//             const result = await response.json();
            
//             if (result.success) {
//                 console.log('✅ Donation recorded in backend:', result);
//                 showSuccessModal(usdAmount, txHash, result.points_earned);
//             } else {
//                 console.error('Backend error:', result.error);
//                 // Still show success since blockchain transaction succeeded
//                 showSuccessModal(usdAmount, txHash, 0);
//             }
//         } catch (apiError) {
//             console.error('Error recording donation:', apiError);
//             // Still show success since blockchain transaction succeeded
//             showSuccessModal(usdAmount, txHash, 0);
//         }
        
//     } catch (error) {
//         console.error('Donation error:', error);
        
//         let errorMessage = 'Transaction failed. Please try again.';
        
//         if (error.code === 4001) {
//             errorMessage = 'Transaction cancelled by user.';
//         } else if (error.code === -32000) {
//             errorMessage = 'Insufficient funds for gas fees.';
//         } else if (error.code === -32602) {
//             errorMessage = 'Invalid transaction parameters.';
//         } else if (error.code === -32603) {
//             errorMessage = 'Internal error. Please try again.';
//         }
        
//         alert(errorMessage);
//         donateBtn.textContent = 'Send Donation';
//     }
// }

// function showSuccessModal(amount, txHash, pointsEarned = 0) {
//     document.getElementById('txHash').textContent = txHash;
//     document.getElementById('donatedAmount').textContent = amount.toFixed(2);
    
//     // Calculate new progress
//     const newRaised = parseFloat(selectedRecipient.raised_amount) + amount;
//     const newProgress = Math.min((newRaised / parseFloat(selectedRecipient.goal_amount)) * 100, 100);
//     document.getElementById('recipientProgress').textContent = `${newProgress.toFixed(1)}%`;
    
//     closeDonationModal();
//     document.getElementById('successModal').classList.remove('hidden');
//     document.getElementById('donateButtonText').textContent = 'Send Donation';
// }

// window.closeSuccessModal = function() {
//     document.getElementById('successModal').classList.add('hidden');
//     // Refresh data
//     loadStats();
//     loadRecipients(1, currentFilter);
// }

// // Share functions
// window.shareRecipient = function(recipientId) {
//     const shareText = `Help someone in need! Every donation makes a difference. 💙`;
//     const shareUrl = `${window.location.origin}/farcaster-mini-app?recipient=${recipientId}`;
    
//     if (navigator.share) {
//         navigator.share({
//             title: 'Help Someone in Need',
//             text: shareText,
//             url: shareUrl,
//         });
//     } else {
//         navigator.clipboard.writeText(`${shareText}\n\n${shareUrl}`);
//         alert('Link copied to clipboard!');
//     }
// }

// window.shareOnFarcaster = function() {
//     const donatedAmount = document.getElementById('donatedAmount').textContent;
//     const recipientName = selectedRecipient ? selectedRecipient.name : 'someone in need';
    
//     const castText = `Just donated ${donatedAmount} to help ${recipientName} through @givebase! 💙 Every act of kindness creates ripples of hope.`;
//     const farcasterUrl = `https://warpcast.com/~/compose?text=${encodeURIComponent(castText)}`;
    
//     window.open(farcasterUrl, '_blank');
// }

// window.loadMoreRecipients = function() {
//     if (hasMoreRecipients) {
//         loadRecipients(currentPage + 1, currentFilter);
//     }
// }

// // Helper functions
// function getCategoryIcon(category) {
//     const icons = {
//         'medical': '🏥',
//         'emergency': '🚨',
//         'education': '🎓',
//         'community': '🏘️',
//         'creators': '🎨',
//         'development': '⚡',
//         'family': '👨‍👩‍👧‍👦',
//         'business': '💼',
//         'housing': '🏠',
//         'other': '💝'
//     };
//     return icons[category] || '💝';
// }

// function getUrgencyClass(level) {
//     if (level >= 4) return 'urgency-high';
//     if (level >= 3) return 'urgency-medium';
//     return 'urgency-low';
// }

// function getUrgencyText(level) {
//     if (level >= 4) return 'URGENT';
//     if (level >= 3) return 'MEDIUM';
//     return 'LOW';
// }

// // Event listeners
// document.addEventListener('DOMContentLoaded', () => {
//     // Set up wallet connect button
//     const connectBtn = document.getElementById('connectWallet');
//     if (connectBtn) {
//         connectBtn.addEventListener('click', handleWalletConnect);
//     }
    
//     // Handle custom amount input
//     const customAmountInput = document.getElementById('customAmount');
//     if (customAmountInput) {
//         customAmountInput.addEventListener('input', function() {
//             if (this.value) {
//                 // Clear preset selection when custom amount is entered
//                 document.querySelectorAll('.quick-donate-btn').forEach(btn => {
//                     btn.classList.remove('selected');
//                 });
//             }
//             updateEstimatedCosts();
//         });
//     }

//     // Initialize default filter
//     const allBtn = document.querySelector('[data-filter="all"]');
//     if (allBtn) {
//         allBtn.classList.remove('secondary-button');
//         allBtn.classList.add('primary-button');
//     }
// });

// // Initialize the app when page loads
// window.addEventListener('load', initializeApp);

// console.log('🌟 GiveBase Farcaster Mini App initialized!');
// console.log('💜 Ready to help people in need with Farcaster wallet!');