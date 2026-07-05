import { Card, Box, Typography, Button, Divider } from '@mui/material';
import FolderIcon from '@mui/icons-material/FolderOpen';
import CodeIcon from '@mui/icons-material/Code';

interface Issue {
  id: string;
  file: string;
  line: number;
  severity: string;
  category: string;
  title: string;
  description: string;
  explanation: string;
  suggested_fix: string;
  confidence: string;
}

interface CodeVisualizerProps {
  fileList: string[];
  issues: Issue[];
  selectedFile: string;
  onFileSelect: (file: string) => void;
  fileContent: string;
}

export default function CodeVisualizer({
  fileList,
  issues,
  selectedFile,
  onFileSelect,
  fileContent
}: CodeVisualizerProps) {
  return (
    <Card sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 2fr' }, overflow: 'hidden' }}>
      {/* File List Panel */}
      <Box sx={{ borderRight: { md: '1px solid rgba(255, 255, 255, 0.05)' }, bgcolor: 'rgba(15, 16, 29, 0.4)', p: 3, maxHeight: 500, overflowY: 'auto' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
          <FolderIcon sx={{ color: '#a855f7', fontSize: 18 }} />
          <Typography variant="caption" sx={{ fontWeight: 700, textTransform: 'uppercase', color: 'text.secondary', letterSpacing: 1.5 }}>
            FILE EXPLORER
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          {fileList.map((file) => {
            const fileIssues = issues.filter((i) => i.file === file);
            const isSelected = selectedFile === file;
            return (
              <Button
                key={file}
                onClick={() => onFileSelect(file)}
                variant="text"
                sx={{
                  justifyContent: 'space-between',
                  px: 2,
                  py: 1,
                  borderRadius: 1.5,
                  fontSize: 11,
                  fontFamily: 'monospace',
                  color: isSelected ? '#a855f7' : 'text.secondary',
                  bgcolor: isSelected ? 'rgba(168, 85, 247, 0.08)' : 'transparent',
                  '&:hover': {
                    bgcolor: isSelected ? 'rgba(168, 85, 247, 0.12)' : 'rgba(255, 255, 255, 0.04)',
                  }
                }}
              >
                <span style={{ textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap', maxWidth: '80%' }}>
                  {file}
                </span>
                {fileIssues.length > 0 && (
                  <Box
                    sx={{
                      fontSize: 9,
                      fontWeight: 700,
                      bgcolor: 'rgba(244, 63, 94, 0.15)',
                      color: '#f43f5e',
                      px: 0.8,
                      py: 0.2,
                      borderRadius: '50%',
                      minWidth: 16,
                      height: 16,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    {fileIssues.length}
                  </Box>
                )}
              </Button>
            );
          })}
        </Box>
      </Box>

      {/* Code Editor Panel */}
      <Box sx={{ p: 4, display: 'flex', flexDirection: 'column', gap: 3, maxHeight: 500, overflowY: 'auto' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CodeIcon sx={{ color: '#06b6d4', fontSize: 18 }} />
          <Typography variant="caption" sx={{ fontWeight: 700, textTransform: 'uppercase', color: 'text.secondary', letterSpacing: 1.5 }}>
            SOURCE PREVIEW: {selectedFile.split('/').pop()}
          </Typography>
        </Box>
        
        <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.05)' }} />

        <Box
          sx={{
            width: '100%',
            overflowX: 'auto',
            bgcolor: '#05060b',
            borderRadius: 3,
            border: '1px solid rgba(255, 255, 255, 0.04)',
            p: 3,
            fontFamily: 'monospace',
            fontSize: 11,
            lineHeight: 1.6,
            color: 'slate.300',
          }}
        >
          {fileContent ? (
            fileContent.split('\n').map((line, idx) => {
              const lineNo = idx + 1;
              const lineIssues = issues.filter((i) => i.file === selectedFile && i.line === lineNo);
              const hasIssues = lineIssues.length > 0;
              
              return (
                <Box
                  key={idx}
                  sx={{
                    display: 'flex',
                    py: 0.25,
                    px: 1,
                    borderRadius: 1,
                    bgcolor: hasIssues ? 'rgba(244, 63, 94, 0.08)' : 'transparent',
                    borderLeft: hasIssues ? '3px solid #f43f5e' : 'none',
                    '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.03)' }
                  }}
                >
                  <Box sx={{ width: 32, color: 'text.muted', textAlign: 'right', pr: 2, userSelect: 'none', opacity: 0.5 }}>
                    {lineNo}
                  </Box>
                  <Box component="pre" sx={{ m: 0, whiteSpace: 'pre', color: hasIssues ? '#f43f5e' : '#f8fafc' }}>
                    {line}
                  </Box>
                  {hasIssues && (
                    <Box
                      sx={{
                        ml: 2,
                        fontSize: 9,
                        fontWeight: 700,
                        bgcolor: 'rgba(244, 63, 94, 0.1)',
                        color: '#f43f5e',
                        px: 1,
                        py: 0.1,
                        borderRadius: 1,
                        alignSelf: 'center',
                        userSelect: 'none'
                      }}
                    >
                      {lineIssues[0].title}
                    </Box>
                  )}
                </Box>
              );
            })
          ) : (
            <Typography variant="caption" sx={{ color: 'text.secondary', textAlign: 'center', py: 6, display: 'block' }}>
              Select a file from the list to preview content.
            </Typography>
          )}
        </Box>
      </Box>
    </Card>
  );
}
