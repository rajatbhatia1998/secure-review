import { AppBar, Toolbar, Typography, Button, Box, Chip } from '@mui/material';
import ShieldIcon from '@mui/icons-material/Shield';
import SettingsIcon from '@mui/icons-material/Settings';
import RestartAltIcon from '@mui/icons-material/RestartAlt';

interface HeaderProps {
  provider: string;
  model: string;
  onOpenConfig: () => void;
  hasReport?: boolean;
  onNewAudit?: () => void;
  onRescan?: () => void;
}

export default function Header({ provider, model, onOpenConfig, hasReport, onNewAudit, onRescan }: HeaderProps) {
  return (
    <AppBar position="sticky" sx={{ background: 'rgba(15, 16, 29, 0.8)', backdropFilter: 'blur(12px)', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', boxShadow: 'none' }}>
      <Toolbar sx={{ justifyContent: 'space-between', px: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box sx={{ p: 1, borderRadius: 2, display: 'flex', background: 'rgba(168, 85, 247, 0.1)', border: '1px solid rgba(168, 85, 247, 0.2)' }}>
            <ShieldIcon sx={{ color: '#a855f7', fontSize: 28 }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 800, letterSpacing: -0.5, lineHeight: 1.2 }}>
              AI Secure Review
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block' }}>
              Multi-Agent Security & Quality Orchestrator
            </Typography>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Chip
            icon={<Box component="span" sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#10b981', display: 'inline-block', mr: 0.5, animation: 'pulse 2s infinite ease-in-out' }} />}
            label={`Mode: ${provider} (${model})`}
            variant="outlined"
            size="small"
            sx={{ border: '1px solid rgba(255, 255, 255, 0.08)', bgcolor: 'rgba(255, 255, 255, 0.02)', color: 'text.secondary', '.MuiChip-icon': { ml: 1 } }}
          />

          {hasReport && onRescan && (
            <Button
              variant="contained"
              size="small"
              startIcon={<RestartAltIcon />}
              onClick={onRescan}
              sx={{
                bgcolor: '#a855f7',
                color: '#f8fafc',
                boxShadow: '0 4px 14px rgba(168, 85, 247, 0.3)',
                '&:hover': {
                  bgcolor: '#7c3aed',
                }
              }}
            >
              Rescan
            </Button>
          )}

          {hasReport && onNewAudit && (
            <Button
              variant="outlined"
              size="small"
              onClick={onNewAudit}
              sx={{
                borderColor: 'rgba(255, 255, 255, 0.1)',
                color: 'text.secondary',
                '&:hover': {
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                  bgcolor: 'rgba(255, 255, 255, 0.05)',
                }
              }}
            >
              New Scan
            </Button>
          )}

          <Button
            variant="text"
            onClick={onOpenConfig}
            sx={{ minWidth: 0, p: 1, color: 'text.secondary', '&:hover': { color: '#f8fafc', bgcolor: 'rgba(255, 255, 255, 0.05)' } }}
          >
            <SettingsIcon />
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
