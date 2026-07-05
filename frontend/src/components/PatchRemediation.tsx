import { Card, CardContent, Typography, Box, Chip, Grid } from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

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

interface PatchRemediationProps {
  selectedIssue: Issue;
}

export default function PatchRemediation({ selectedIssue }: PatchRemediationProps) {
  const getSeverityStyle = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
      case 'HIGH':
        return { bg: 'rgba(244, 63, 94, 0.1)', color: '#f43f5e', border: '1px solid rgba(244, 63, 94, 0.2)' };
      case 'MEDIUM':
        return { bg: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b', border: '1px solid rgba(245, 158, 11, 0.2)' };
      default:
        return { bg: 'rgba(16, 185, 129, 0.1)', color: '#10b981', border: '1px solid rgba(16, 185, 129, 0.2)' };
    }
  };

  const chipStyle = getSeverityStyle(selectedIssue.severity);

  // Helper to parse markdown code blocks and render them in stylized blocks
  const renderFormattedText = (text: string) => {
    if (!text) return null;
    
    const parts = text.split(/```/);
    return parts.map((part, index) => {
      if (index % 2 === 1) {
        // Code Block
        const lines = part.split('\n');
        const firstLine = lines[0].trim();
        const isLang = ['python', 'javascript', 'typescript', 'go', 'rust', 'html', 'css', 'json', 'sh', 'bash', 'sql'].includes(firstLine);
        const codeContent = isLang ? lines.slice(1).join('\n') : part;
        
        return (
          <Box
            key={index}
            component="pre"
            sx={{
              p: 2.5,
              my: 2,
              bgcolor: '#04040a',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              borderRadius: 3,
              overflowX: 'auto',
              fontFamily: 'Consolas, Monaco, "Andale Mono", monospace',
              fontSize: '0.8rem',
              color: '#c084fc',
              boxShadow: 'inset 0 2px 10px rgba(0,0,0,0.8)'
            }}
          >
            <code>{codeContent.trim()}</code>
          </Box>
        );
      }
      
      // Standard Text
      return (
        <span key={index} style={{ whiteSpace: 'pre-wrap' }}>
          {part}
        </span>
      );
    });
  };

  return (
    <Card>
      <CardContent sx={{ p: 4, display: 'flex', flexDirection: 'column', gap: 3.5 }}>
        {/* Metadata Bar */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', pb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Chip
              label={selectedIssue.severity}
              size="small"
              sx={{
                fontSize: 9,
                fontWeight: 800,
                bgcolor: chipStyle.bg,
                color: chipStyle.color,
                border: chipStyle.border
              }}
            />
            <Typography variant="caption" sx={{ fontWeight: 700, color: '#a855f7', textTransform: 'uppercase', letterSpacing: 1 }}>
              {selectedIssue.category}
            </Typography>
          </Box>
          <Typography variant="caption" sx={{ color: 'text.secondary', fontFamily: 'monospace' }}>
            {selectedIssue.file}:{selectedIssue.line}
          </Typography>
        </Box>

        {/* Title and description */}
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          <Typography variant="h6" sx={{ fontWeight: 800, letterSpacing: -0.5, color: '#f8fafc' }}>
            {selectedIssue.title}
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.6 }}>
            {selectedIssue.description}
          </Typography>
        </Box>

        {/* Dual Info Section */}
        <Grid container spacing={3} sx={{ pt: 1 }}>
          <Grid size={{ xs: 12, md: 6 }}>
            <Box sx={{ p: 3, borderRadius: 3, bgcolor: 'rgba(15, 16, 29, 0.3)', border: '1px solid rgba(255, 255, 255, 0.04)', height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                <InfoIcon sx={{ color: '#06b6d4', fontSize: 16 }} />
                <Typography variant="caption" sx={{ fontWeight: 700, color: '#06b6d4', textTransform: 'uppercase', letterSpacing: 1.2 }}>
                  AI Technical Explanation
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ color: 'text.secondary', fontSize: 12, lineHeight: 1.6 }}>
                {renderFormattedText(selectedIssue.explanation)}
              </Typography>
            </Box>
          </Grid>
          
          <Grid size={{ xs: 12, md: 6 }}>
            <Box sx={{ p: 3, borderRadius: 3, bgcolor: 'rgba(15, 16, 29, 0.3)', border: '1px solid rgba(255, 255, 255, 0.04)', height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                <CheckCircleIcon sx={{ color: '#10b981', fontSize: 16 }} />
                <Typography variant="caption" sx={{ fontWeight: 700, color: '#10b981', textTransform: 'uppercase', letterSpacing: 1.2 }}>
                  Remediation Recommendation
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ color: 'text.primary', fontSize: 12, lineHeight: 1.6 }}>
                {renderFormattedText(selectedIssue.suggested_fix)}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}
