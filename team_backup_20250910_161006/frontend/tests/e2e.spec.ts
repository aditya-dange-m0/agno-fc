import { test, expect } from '@playwright/test';

test('User can login', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.click('text=Login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'password');
  await page.click('button');
  await expect(page).toHaveURL('http://localhost:3000/dashboard');
});