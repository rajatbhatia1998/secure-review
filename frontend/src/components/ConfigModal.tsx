import { Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button, Select, MenuItem, FormControl, InputLabel, Typography } from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';

interface LLMConfig {
  provider: string;
  base_url: string;
  model: string;
  api_key: string;
  temperature: number;
}

interface ConfigModalProps {
  config: LLMConfig;
  setConfig: (cfg: LLMConfig) => void;
  providers: string[];
  saveStatus: string;
  onSave: (e: React.FormEvent) => void;
  onClose: () => void;
}

export default function ConfigModal({
  config,
  setConfig,
  providers,
  saveStatus,
  onSave,
  onClose
}: ConfigModalProps) {
  const providerDetails: Record<string, { label: string; defaultUrl: string; placeholderModel: string }> = {
    openai: { label: 'OpenAI (GPT-4o)', defaultUrl: 'https://api.openai.com/v1', placeholderModel: 'gpt-4o-mini' },
    gemini: { label: 'Gemini (Google)', defaultUrl: 'https://generativelanguage.googleapis.com/v1beta/openai/', placeholderModel: 'gemini-1.5-flash' },
    anthropic: { label: 'Anthropic (Claude)', defaultUrl: 'https://api.anthropic.com', placeholderModel: 'claude-3-5-sonnet-20241022' },
    groq: { label: 'Groq (GroqCloud)', defaultUrl: 'https://api.groq.com/openai/v1', placeholderModel: 'llama-3.3-70b-versatile' },
    ollama: { label: 'Ollama (Local Offline)', defaultUrl: 'http://localhost:11434', placeholderModel: 'llama3.1' },
    lmstudio: { label: 'LM Studio (Local Offline)', defaultUrl: 'http://localhost:1234/v1', placeholderModel: 'llama3.1' }
  };

  const handleProviderChange = (prov: string) => {
    const details = providerDetails[prov] || { defaultUrl: '', placeholderModel: '' };
    setConfig({
      ...config,
      provider: prov,
      base_url: details.defaultUrl,
      model: details.placeholderModel
    });
  };

  const isCloudProvider = ['openai', 'gemini', 'anthropic', 'groq'].includes(config.provider);

  return (
    <Dialog
      open={true}
      onClose={onClose}
      maxWidth="xs"
      fullWidth
      slotProps={{
        paper: {
          sx: {
            bgcolor: 'background.paper',
            backgroundImage: 'none',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            borderRadius: 4,
            p: 1
          }
        }
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1.5, fontWeight: 800 }}>
        <SettingsIcon sx={{ color: '#a855f7' }} />
        <span>LLM Model Setup</span>
      </DialogTitle>

      <form onSubmit={onSave}>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          <FormControl fullWidth size="small">
            <InputLabel id="provider-select-label">Model Provider</InputLabel>
            <Select
              labelId="provider-select-label"
              value={config.provider}
              label="Model Provider"
              onChange={(e) => handleProviderChange(e.target.value)}
            >
              {providers.map((p) => (
                <MenuItem key={p} value={p}>
                  {providerDetails[p]?.label || p.toUpperCase()}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {!isCloudProvider && (
            <TextField
              fullWidth
              size="small"
              label="API Endpoint URL"
              value={config.base_url}
              onChange={(e) => setConfig({ ...config, base_url: e.target.value })}
              placeholder="http://localhost:11434"
            />
          )}

          <TextField
            fullWidth
            size="small"
            label="Model Name"
            value={config.model}
            onChange={(e) => setConfig({ ...config, model: e.target.value })}
            placeholder={providerDetails[config.provider]?.placeholderModel || 'llama3.1'}
          />

          <TextField
            fullWidth
            size="small"
            type="password"
            label={isCloudProvider ? 'API Key (Required)' : 'API Key (Optional)'}
            value={config.api_key}
            onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
            placeholder={isCloudProvider ? 'sk-...' : 'Leave blank if local'}
          />

          {saveStatus && (
            <Typography
              variant="caption"
              sx={{
                color: saveStatus.includes('successfully') ? '#10b981' : '#f43f5e',
                fontWeight: 600,
                textAlign: 'center',
                display: 'block'
              }}
            >
              {saveStatus}
            </Typography>
          )}
        </DialogContent>

        <DialogActions sx={{ p: 3, pt: 1, gap: 1 }}>
          <Button onClick={onClose} color="inherit" size="small">
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            size="small"
            sx={{
              bgcolor: '#a855f7',
              boxShadow: '0 4px 14px rgba(168, 85, 247, 0.3)',
              '&:hover': { bgcolor: '#7c3aed' }
            }}
          >
            Save Configuration
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
