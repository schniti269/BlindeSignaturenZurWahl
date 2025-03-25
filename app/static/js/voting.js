// Global variables to store state
let publicKey = null;
let dhParams = null;
let sharedKey = null;
let blindedBallot = null;
let originalBallot = null;
let blindSignature = null;
let unblindedSignature = null;
let studentId = null;
let clientId = null;
let originalText = null;

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

// Generate a random client ID
function generateClientId() {
    return 'client_' + Math.random().toString(36).substring(2, 15);
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Generate a unique client ID for this session
    clientId = generateClientId();
    console.log('Client ID:', clientId);
    
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
            // Speichere sowohl den Originaltext als auch den numerischen Wert
            originalText = choice;
            
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
    
    // Step 3: Generate DH parameters and blind the ballot
    document.getElementById('btn-step3').addEventListener('click', function() {
        try {
            // Generate DH parameters
            const p = BigInt(publicKey.p);
            const g = BigInt(publicKey.g);
            
            // Generate random 'a' for DH
            const a = BigInt(Math.floor(Math.random() * 1000) + 100);
            
            // Calculate A = g^a mod p
            const A = modPow(g, a, p);
            
            dhParams = {
                a: a,
                A: A
            };
            
            document.getElementById('blinding-factor').textContent = "DH parameter a: " + a.toString();
            
            // Send A to server and get B
            fetch('/dh-exchange', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    client_id: clientId,
                    A: A.toString()
                })
            })
            .then(response => response.json())
            .then(data => {
                // Calculate shared key K = B^a mod p
                const B = BigInt(data.B);
                sharedKey = modPow(B, dhParams.a, p);
                
                // Speichere sharedKey explizit als String für spätere Konvertierung
                sharedKey = sharedKey.toString();
                
                // Blind the ballot: M_blind = (M * K) mod p
                const message = BigInt(originalBallot);
                const sharedKey_bigint = BigInt(sharedKey);
                blindedBallot = (message * sharedKey_bigint) % p;
                
                // Display the results
                document.getElementById('blinded-ballot').textContent = 
                    "B: " + B.toString() + "\n" +
                    "Shared Key K: " + sharedKey + "\n" +
                    "Blinded Ballot: " + blindedBallot.toString();
                
                // Show next button
                document.getElementById('btn-step3').style.display = 'none';
                document.getElementById('btn-step3-next').style.display = 'inline-block';
            })
            .catch(error => {
                console.error('Error in DH exchange:', error);
                alert('Fehler beim Diffie-Hellman-Schlüsselaustausch.');
            });
        } catch (error) {
            console.error('Error blinding ballot:', error);
            alert('Fehler beim Blenden des Stimmzettels: ' + error.message);
        }
    });
    
    document.getElementById('btn-step3-next').addEventListener('click', function() {
        // Move to step 4
        document.getElementById('blinded-ballot-to-auth').textContent = blindedBallot.toString();
        moveToStep(4);
    });
    
    // Step 4: Send to authority
    document.getElementById('btn-step4').addEventListener('click', function() {
        // Reset previous errors
        document.getElementById('auth-error').style.display = 'none';
        
        // Send the blinded ballot to the authority
        fetch('/sign-ballot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                student_id: studentId,
                client_id: clientId,
                blinded_ballot: blindedBallot.toString()
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
        try {
            // Unblind the signature
            const p = BigInt(publicKey.p);
            const blindSig = BigInt(blindSignature);
            
            // Stellen sicher, dass sharedKey ein BigInt ist
            const sharedKey_bigint = typeof sharedKey === 'bigint' ? sharedKey : BigInt(sharedKey);
            
            // Calculate inverse of shared key K^-1 mod p
            // Note: This is a simplification. In a real implementation, we'd need K^x
            // Nutze BigInt Literal 2n statt Number 2
            const K_inv = modPow(sharedKey_bigint, p - 2n, p); // Fermat's little theorem
            
            // Debugging-Ausgaben
            console.log('p:', p);
            console.log('blindSig:', blindSig);
            console.log('sharedKey:', sharedKey_bigint);
            console.log('K_inv:', K_inv);
            
            // Unblind: S = S_blind * K^-1 mod p
            const unblinded = (blindSig * K_inv) % p;
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
        // Reset previous errors
        document.getElementById('vote-error').style.display = 'none';
        
        // Submit the vote
        fetch('/submit-vote', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                vote: originalBallot,
                signature: unblindedSignature,
                candidate: originalText // Sende den lesbaren Kandidatennamen für die Anzeige
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