/**
 * Debug script to test API connectivity
 * Run this in browser console to diagnose API issues
 */

// Test 1: Check environment variables
console.log('=== Environment Check ===');
console.log('VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL);
console.log('VITE_NODE_ENV:', import.meta.env.VITE_NODE_ENV);

// Test 2: Test direct fetch to backend
console.log('\n=== Direct Fetch Test ===');
fetch('http://localhost:8000/health')
  .then(res => res.json())
  .then(data => console.log('Backend health check:', data))
  .catch(err => console.error('Backend health check failed:', err));

// Test 3: Test API endpoint
console.log('\n=== API Endpoint Test ===');
fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'test@example.com',
    password: 'password123',
  }),
})
  .then(res => {
    console.log('Response status:', res.status);
    return res.json();
  })
  .then(data => console.log('Login response:', data))
  .catch(err => console.error('Login failed:', err));

export {};
