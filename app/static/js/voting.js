// Global variables to store state
let publicKey = null;
let blinder = null;
let blindingFactor = null;
let originalBallot = null;
let blindSignature = null;
let unblindedSignature = null;
let studentId = null;

// BigInt version of modular inverse
function modInverseBigInt(a, m) {
    if (typeof a !== 'bigint') a = BigInt(a);
    if (typeof m !== 'bigint') m = BigInt(m);
    
    // Ensure positive a
    a = ((a % m) + m) % m;
    
    // Extended Euclidean Algorithm for BigInt
    let [old_r, r] = [a, m];
    let [old_s, s] = [1n, 0n];
    let [old_t, t] = [0n, 1n];

    while (r !== 0n) {
        const quotient = old_r / r;
        [old_r, r] = [r, old_r - quotient * r];
        [old_s, s] = [s, old_s - quotient * s];
        [old_t, t] = [t, old_t - quotient * t];
    }

    // If gcd is not 1, there's no inverse
    if (old_r !== 1n) {
        return null;
    }

    // Make sure old_s is positive
    return (old_s % m + m) % m;
}

// Legacy modular inverse implementation (keep for compatibility)
function modInverse(a, m) {
    // Validate inputs
    [a, m] = [Number(a), Number(m)];
    if (Number.isNaN(a) || Number.isNaN(m)) {
        return NaN;
    }
    
    a = (a % m + m) % m;
    if (!a || m < 2) {
        return NaN;
    }
    
    // Find the gcd
    const s = [];
    let b = m;
    while(b) {
        [a, b] = [b, a % b];
        s.push({a, b});
    }
    if (a !== 1) {
        return NaN;
    }
    
    // Find the inverse
    let x = 1;
    let y = 0;
    for(let i = s.length - 2; i >= 0; --i) {
        [x, y] = [y,  x - y * Math.floor(s[i].a / s[i].b)];
    }
    return (y % m + m) % m;
}

// GCD function for checking coprime
function gcd(a, b) {
    while (b) {
        [a, b] = [b, a % b];
    }
    return a;
}

// Function to convert string to large integer
function stringToInt(str) {
    let result = 0n;
    for (let i = 0; i < str.length; i++) {
        result = result * 256n + BigInt(str.charCodeAt(i));
    }
    return result;
}

// Power with modulo for large numbers
function modPow(base, exponent, modulus) {
    if (modulus === 1n) return 0n;
    
    let result = 1n;
    base = base % modulus;
    
    while (exponent > 0n) {
        if (exponent % 2n === 1n) {
            result = (result * base) % modulus;
        }
        exponent = exponent >> 1n;
        base = (base * base) % modulus;
    }
    
    return result;
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

function setupEventListeners() {
    // Step 1: Student ID
    document.getElementById('btn-step1').addEventListener('click', function() {
        studentId = document.getElementById('student-id').value.trim();
        if (!studentId) {
            alert('Bitte gib deine Matrikelnummer ein.');
            return;
        }
        
        // Move to step 2
        moveToStep(2);
    });
    
    // Step 2: Create ballot
    document.getElementById('ballot-choice').addEventListener('change', function() {
        const choice = this.value;
        if (choice) {
            // Convert choice to an integer for cryptographic operations
            originalBallot = stringToInt(choice).toString();
            document.getElementById('raw-ballot').value = originalBallot;
        }
    });
    
    document.getElementById('btn-step2').addEventListener('click', function() {
        if (!document.getElementById('raw-ballot').value) {
            alert('Bitte wähle einen Kandidaten.');
            return;
        }
        
        // Fetch the public key from the server
        fetch('/get-public-key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            publicKey = data.public_key;
            document.getElementById('auth-public-key').textContent = JSON.stringify(publicKey, null, 2);
            moveToStep(3);
        })
        .catch(error => {
            console.error('Error fetching public key:', error);
            alert('Fehler beim Abrufen des Public Keys.');
        });
    });
    
    // Step 3: Blind the ballot
    document.getElementById('btn-step3').addEventListener('click', function() {
        // Blind the ballot
        const n = BigInt(publicKey.n);
        const e = BigInt(publicKey.e);
        
        // Generate random blinding factor
        let r;
        do {
            // Use a simpler random number for demo purposes
            r = BigInt(Math.floor(Math.random() * 1000000) + 100000);
        } while (gcd(Number(r), Number(n)) !== 1);
        
        blindingFactor = r;
        
        // Calculate r^e mod n
        const r_e = modPow(r, e, n);
        
        // Blind the message: (message * r^e) mod n
        const message = BigInt(originalBallot);
        const blindedMessage = (message * r_e) % n;
        
        // Display the results
        document.getElementById('blinding-factor').textContent = blindingFactor.toString();
        document.getElementById('blinded-ballot').textContent = blindedMessage.toString();
        blinder = blindedMessage.toString();
        
        // Show next button
        document.getElementById('btn-step3').style.display = 'none';
        document.getElementById('btn-step3-next').style.display = 'inline-block';
    });
    
    document.getElementById('btn-step3-next').addEventListener('click', function() {
        // Move to step 4
        document.getElementById('blinded-ballot-to-auth').textContent = blinder;
        moveToStep(4);
    });
    
    // Step 4: Send to authority
    document.getElementById('btn-step4').addEventListener('click', function() {
        // Send the blinded ballot to the authority
        fetch('/sign-ballot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                student_id: studentId,
                blinded_ballot: blinder
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            // Display the blind signature
            blindSignature = data.blind_signature;
            document.getElementById('blind-signature').textContent = blindSignature;
            document.getElementById('blind-signature-container').style.display = 'block';
            
            // Show next button
            document.getElementById('btn-step4').style.display = 'none';
            document.getElementById('btn-step4-next').style.display = 'inline-block';
        })
        .catch(error => {
            console.error('Error getting signature:', error);
            document.getElementById('auth-error').textContent = error.error || 'Fehler bei der Signierung.';
            document.getElementById('auth-error').style.display = 'block';
        });
    });
    
    document.getElementById('btn-step4-next').addEventListener('click', function() {
        // Move to step 5
        document.getElementById('blind-sig-to-unblind').textContent = blindSignature;
        moveToStep(5);
    });
    
    // Step 5: Unblind signature
    document.getElementById('btn-step5').addEventListener('click', function() {
        // Unblind the signature
        try {
            const n = BigInt(publicKey.n);
            const blindSig = BigInt(blindSignature);
            const r = BigInt(blindingFactor);
            
            // Calculate r^-1 mod n using BigInt version
            const r_inv = modInverseBigInt(r, n);
            
            if (r_inv === null) {
                alert('Fehler bei der Berechnung des multiplikativen Inversen. Die Zahlen sind möglicherweise nicht teilerfremd.');
                return;
            }
            
            // Unblind: (blindSig * r_inv) mod n
            const unblinded = (blindSig * r_inv) % n;
            unblindedSignature = unblinded.toString();
            
            // Display the unblinded signature
            document.getElementById('unblinded-signature').textContent = unblindedSignature;
            document.getElementById('unblinded-signature-container').style.display = 'block';
            
            // Show next button
            document.getElementById('btn-step5').style.display = 'none';
            document.getElementById('btn-step5-next').style.display = 'inline-block';
        } catch (error) {
            console.error('Error during unblinding:', error);
            alert('Fehler beim Entblenden: ' + error.message);
        }
    });
    
    document.getElementById('btn-step5-next').addEventListener('click', function() {
        // Move to step 6
        document.getElementById('final-ballot').textContent = originalBallot;
        document.getElementById('final-signature').textContent = unblindedSignature;
        moveToStep(6);
    });
    
    // Step 6: Submit vote
    document.getElementById('btn-step6').addEventListener('click', function() {
        // Submit the vote
        fetch('/submit-vote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                vote: originalBallot,
                signature: unblindedSignature
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            // Show success message
            document.getElementById('vote-success').style.display = 'block';
            document.getElementById('btn-step6').style.display = 'none';
            document.getElementById('btn-finish').style.display = 'inline-block';
        })
        .catch(error => {
            console.error('Error submitting vote:', error);
            document.getElementById('vote-error').textContent = error.error || 'Fehler bei der Stimmabgabe.';
            document.getElementById('vote-error').style.display = 'block';
        });
    });
}

function moveToStep(stepNumber) {
    // Hide all steps
    for (let i = 1; i <= 6; i++) {
        const step = document.getElementById(`step${i}`);
        step.classList.remove('step-active');
        step.classList.add('step-inactive');
        if (i < stepNumber) {
            step.classList.add('step-completed');
        }
    }
    
    // Show the current step
    const currentStep = document.getElementById(`step${stepNumber}`);
    currentStep.classList.remove('step-inactive');
    currentStep.classList.add('step-active');
} 