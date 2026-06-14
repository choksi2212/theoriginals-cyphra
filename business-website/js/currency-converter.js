// Currency Conversion and Pricing Update Script
// Converts all USD to INR and updates pricing to be very cheap with maximum profit

const USD_TO_INR = 83; // Current exchange rate

// New ultra-cheap pricing with maximum profit margins
const NEW_PRICING = {
    pro_monthly: 49, // ₹49/month (was $4.99 = ₹414)
    pro_annual: 499, // ₹499/year (was $49.99 = ₹4149)
    enterprise_monthly: 149, // ₹149/user/month (was $12.99 = ₹1078)
    
    // Cost structure (ultra-low to maximize profit)
    infrastructure_per_user: 0.50, // ₹0.50 per user per month
    support_per_user: 0.25, // ₹0.25 per user per month
    
    // Profit margins
    pro_margin: 98.5, // 98.5% profit margin
    enterprise_margin: 99.5 // 99.5% profit margin
};

// Function to convert USD amount to INR
function convertToINR(usdAmount) {
    return Math.round(usdAmount * USD_TO_INR);
}

// Function to format INR currency
function formatINR(amount) {
    return '₹' + amount.toLocaleString('en-IN');
}

// Function to update all currency values on page load
function updateAllCurrencyValues() {
    // Update all text content with USD amounts
    const bodyText = document.body.innerHTML;
    
    // Replace $X,XXX,XXX patterns
    let updatedText = bodyText.replace(/\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)(M|K|B)?/g, function(match, amount, suffix) {
        let numAmount = parseFloat(amount.replace(/,/g, ''));
        
        if (suffix === 'M') numAmount *= 1000000;
        else if (suffix === 'K') numAmount *= 1000;
        else if (suffix === 'B') numAmount *= 1000000000;
        
        let inrAmount = convertToINR(numAmount);
        
        // Format with suffix
        if (inrAmount >= 10000000) { // 1 Crore
            return formatINR(Math.round(inrAmount / 10000000)) + ' Cr';
        } else if (inrAmount >= 100000) { // 1 Lakh
            return formatINR(Math.round(inrAmount / 100000)) + ' L';
        } else if (inrAmount >= 1000) {
            return formatINR(Math.round(inrAmount / 1000)) + 'K';
        } else {
            return formatINR(inrAmount);
        }
    });
    
    document.body.innerHTML = updatedText;
}

// Run on page load
document.addEventListener('DOMContentLoaded', updateAllCurrencyValues);
