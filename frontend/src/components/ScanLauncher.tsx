import { useState } from 'react';
import { Card, CardContent, Typography, TextField, Button, Box, InputAdornment } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';

interface ScanLauncherProps {
  repoPath: string;
  setRepoPath: (val: string) => void;
  isScanning: boolean;
  onScan: () => void;
  apiHealth: boolean | null;
}

export default function ScanLauncher({
  repoPath,
  setRepoPath,
  isScanning,
  onScan,
  apiHealth
}: ScanLauncherProps) {
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoPath || !repoPath.trim()) {
      setError('Repository folder path is required.');
      return;
    }
    setError('');
    onScan();
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
      <Card sx={{ width: '100%', maxWidth: 600, bgcolor: 'background.paper', borderRadius: 4 }}>
        <CardContent sx={{ p: 5 }}>
          <Typography variant="h5" sx={{ fontWeight: 800, mb: 1, letterSpacing: -0.5 }}>
            Security Audit Launcher
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary', mb: 4 }}>
            Input the path of a local project directory to map the files and run code analyses.
          </Typography>

          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <TextField
                fullWidth
                label="Local Folder Path"
                variant="outlined"
                value={repoPath}
                onChange={(e) => setRepoPath(e.target.value)}
                error={!!error}
                helperText={error}
                placeholder="C:/Users/name/projects/my-app"
                slotProps={{
                  input: {
                    startAdornment: (
                      <InputAdornment position="start">
                        <FolderOpenIcon sx={{ color: 'text.secondary' }} />
                      </InputAdornment>
                    ),
                  },
                }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    bgcolor: 'rgba(255, 255, 255, 0.02)',
                    '& fieldset': { borderColor: 'rgba(255, 255, 255, 0.08)' },
                    '&:hover fieldset': { borderColor: 'rgba(255, 255, 255, 0.15)' },
                  }
                }}
              />

              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      bgcolor: apiHealth ? '#10b981' : (apiHealth === false ? '#f43f5e' : '#f59e0b'),
                      animation: 'pulse 2s infinite ease-in-out'
                    }}
                  />
                  <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                    {apiHealth ? 'Service API: Connected' : (apiHealth === false ? 'Service API: Offline' : 'Service API: Reconnecting...')}
                  </Typography>
                </Box>

                <Button
                  type="submit"
                  variant="contained"
                  disabled={isScanning || apiHealth === false}
                  startIcon={<PlayArrowIcon />}
                  sx={{
                    bgcolor: '#a855f7',
                    fontWeight: 700,
                    px: 3,
                    py: 1.2,
                    boxShadow: '0 4px 14px rgba(168, 85, 247, 0.3)',
                    '&:hover': {
                      bgcolor: '#7c3aed',
                      boxShadow: '0 6px 20px rgba(168, 85, 247, 0.5)',
                    }
                  }}
                >
                  Start Audit
                </Button>
              </Box>
            </Box>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}
