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

    await expect(api.get('/error-endpoint')).rejects.toThrow('HTTP 500');
  });

  it('extracts detail message when present', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ detail: 'Policy with this name already exists.' })
    } as Response);

    await expect(api.get('/error-endpoint')).rejects.toThrow('Policy with this name already exists.');
  });

  it('dispatches unauthorized event on 401', async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'Unauthorized' })
    } as Response);

    await expect(api.get('/forbidden')).rejects.toMatchObject({ status: 401 });
  });
});
