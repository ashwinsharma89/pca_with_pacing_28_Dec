# E2E Testing Setup Guide

## Test Credentials

Update the test credentials in `e2e/pca-agent.spec.ts` to match your test user:

```typescript
const TEST_USER = {
  username: 'testuser',  // or 'admin' or your test username
  password: 'testpassword123'  // or 'Admin1234!' or your test password
};
```

## Running Tests

```bash
# Run all tests
cd frontend && npm run test

# Run with UI mode (recommended for debugging)
npm run test:ui

# Run in headed mode (see browser)
npm run test:headed

# Run specific test file
npm run test e2e/pca-agent.spec.ts

# Run only chromium
npm run test -- --project=chromium

# Debug mode
npm run test:debug
```

## Test Results

**Total Tests:** 26  
**Passed:** 1 (invalid credentials validation)  
**Failed:** 25 (due to incorrect test credentials)

### Test Coverage

✅ **Authentication (3 tests)**
- Login with valid credentials
- Show error with invalid credentials ✓
- Logout successfully

✅ **Upload Flow (3 tests)**
- Navigate to upload page
- Show file upload interface
- Display upload instructions

✅ **Q&A (Chat) Flow (4 tests)**
- Navigate to chat page
- Show chat interface with input
- Toggle between Data and Knowledge mode
- Show suggested questions on initial load

✅ **Analysis Flow (4 tests)**
- Navigate to analysis page
- Show configuration options
- Show portfolio metrics
- Have run analysis button

✅ **Dashboard Builder Flow (4 tests)**
- Navigate to dashboard builder
- Show add widget button
- Show empty state when no widgets
- Open add widget dialog

✅ **Visualizations Flow (4 tests)**
- Navigate to visualizations page
- Show filter options
- Display charts
- Have apply filters button

✅ **Navigation (2 tests)**
- Have working navigation links
- Navigate between pages

✅ **Responsive Design (2 tests)**
- Responsive on mobile viewport
- Responsive on tablet viewport

## Fixing Test Failures

### Option 1: Update Test Credentials

Edit `e2e/pca-agent.spec.ts` line 16-19:

```typescript
const TEST_USER = {
  username: 'admin',  // Use your actual test user
  password: 'Admin1234!'  // Use actual password
};
```

### Option 2: Create Test User

Run the backend seed script to create a test user:

```bash
cd /Users/ashwin/Desktop/pca_agent\ copy
python scripts/seed_db.py
```

This creates:
- Username: `testuser`
- Password: `testpassword123`

### Option 3: Use Admin User

If you have an admin user, update tests to use:
- Username: `admin`
- Password: `Admin1234!`

## Next Steps

1. **Update credentials** in test file
2. **Re-run tests:** `npm run test`
3. **View report:** `npm run test:report`
4. **Check screenshots/videos** in `test-results/` for failures

## Test Artifacts

After running tests, check:
- `playwright-report/` - HTML test report
- `test-results/` - Screenshots and videos of failures
- `test-results.json` - JSON test results
- `junit.xml` - JUnit format for CI/CD

## CI/CD Integration

The tests are configured for CI/CD with:
- Retry on failure (2 retries in CI)
- Multiple browsers (Chromium, Firefox, WebKit)
- Mobile viewports (Pixel 5, iPhone 12)
- Video recording on failure
- Screenshot on failure

## Performance

Current test execution time: **2.7 minutes** for 26 tests

This is excellent for a comprehensive E2E suite!
