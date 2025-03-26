// QR Code generator using qrcode.js library
document.addEventListener('DOMContentLoaded', function() {
    const qrCodeContainer = document.getElementById('qr-code-js-container');
    if (!qrCodeContainer) return;
    
    // Create a QR code for the site URL
    const siteUrl = 'http://141.72.12.183:33059/';
    
    // Use QRCode.js library if available
    if (typeof QRCode !== 'undefined') {
        new QRCode(qrCodeContainer, {
            text: siteUrl,
            width: 180,
            height: 180,
            colorDark: "#000000",
            colorLight: "#ffffff",
            correctLevel: QRCode.CorrectLevel.L
        });
        console.log("JS QR code generated successfully");
    } else {
        console.log("QRCode library not loaded");
    }
}); 