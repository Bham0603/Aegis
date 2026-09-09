import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api } from '../api';

describe('API Client', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
    sessionStorage.clear();
  });

  it('includes Authorization header if token exists', async () => {
    sessionStorage.setItem('aegis_api_key', 'test-token');
    
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true })
    } as Response);

    await api.get('/test-endpoint');

    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/test-endpoint', expect.any(Object));
  });

  it('throws error on non-ok response', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ error: 'Internal error' })
    } as Response);

    await expect(api.get('/error-endpoint')).rejects.toThrow('API request failed with status 500');
  });
});
