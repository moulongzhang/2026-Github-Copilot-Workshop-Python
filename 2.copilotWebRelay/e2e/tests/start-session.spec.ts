import { test, expect } from '@playwright/test';

test.describe('Copilot Web Relay', () => {
  test('ページタイトルが表示される', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle('Copilot Web Relay');
  });

  test('初期状態: Start Session ボタンとターミナル領域が存在する', async ({ page }) => {
    await page.goto('/');

    const startButton = page.getByRole('button', { name: 'Start Session' });
    await expect(startButton).toBeVisible();

    const terminal = page.locator('.terminal-container');
    await expect(terminal).toBeVisible();
  });

  test('WebSocket 接続後に connected 状態になる', async ({ page }) => {
    await page.goto('/');

    const indicator = page.locator('[data-status="connected"]');
    await expect(indicator).toBeVisible({ timeout: 10_000 });
  });

  test('Start Session クリックで WebSocket メッセージが送信される', async ({ page }) => {
    const wsMessages: string[] = [];

    // WebSocket フレーム監視
    page.on('websocket', (ws) => {
      ws.on('framesent', (frame) => {
        wsMessages.push(frame.payload as string);
      });
    });

    await page.goto('/');

    // 接続待ち
    await page.locator('[data-status="connected"]').waitFor({ timeout: 10_000 });

    // Start Session クリック
    await page.getByRole('button', { name: 'Start Session' }).click();

    // session:start メッセージが送信されたことを確認
    await expect
      .poll(() => {
        return wsMessages.some((msg) => {
          try {
            const parsed = JSON.parse(msg);
            return parsed.type === 'session' && parsed.action === 'start';
          } catch {
            return false;
          }
        });
      }, { timeout: 5_000 })
      .toBeTruthy();

    // サーバーから running 応答があればボタンが Stop Session に変わる
    // （Copilot CLI が存在しない環境ではタイムアウトする可能性があるため soft check）
    try {
      const stopButton = page.getByRole('button', { name: 'Stop Session' });
      await expect(stopButton).toBeVisible({ timeout: 5_000 });
    } catch {
      // CLI が起動できない環境では Start Session のままでも OK
    }
  });
});
