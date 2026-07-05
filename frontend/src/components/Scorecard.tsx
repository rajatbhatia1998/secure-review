import { Card, CardContent, Typography, Box, CircularProgress, LinearProgress } from '@mui/material';

interface ScorecardProps {
  overallScore: number;
  totalFindings: number;
  totalFiles: number;
  categoryScores: Record<string, number>;
}

export default function Scorecard({
  overallScore,
  totalFindings,
  totalFiles,
  categoryScores
}: ScorecardProps) {
  const getScoreColor = (score: number) => {
    if (score >= 90) return '#10b981'; // Emerald
    if (score >= 75) return '#06b6d4'; // Cyan
    if (score >= 60) return '#f59e0b'; // Amber
    return '#f43f5e'; // Rose
  };

  const scoreColor = getScoreColor(overallScore);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Overall Score */}
      <Card>
        <CardContent sx={{ p: 4, display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
          <Typography variant="caption" sx={{ fontWeight: 700, textTransform: 'uppercase', color: 'text.secondary', letterSpacing: 1.5, mb: 3 }}>
            SECURITY SCORECARD
          </Typography>
          
          <Box sx={{ position: 'relative', display: 'inline-flex', mb: 3 }}>
            <CircularProgress
              variant="determinate"
              value={100}
              size={120}
              thickness={4}
              sx={{ color: 'rgba(255, 255, 255, 0.05)' }}
            />
            <CircularProgress
              variant="determinate"
              value={overallScore}
              size={120}
              thickness={4}
              sx={{
                color: scoreColor,
                position: 'absolute',
                left: 0,
                boxShadow: `0 0 16px ${scoreColor}20`,
                circle: { strokeLinecap: 'round' }
              }}
            />
            <Box
              sx={{
                top: 0,
                left: 0,
                bottom: 0,
                right: 0,
                position: 'absolute',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Typography variant="h4" sx={{ fontWeight: 900, color: scoreColor }}>
                {overallScore}
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary', fontSize: 9, fontWeight: 700, textTransform: 'uppercase' }}>
                OVERALL
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ width: '100%', mt: 1, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', pb: 1 }}>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>Findings:</Typography>
              <Typography variant="caption" sx={{ fontWeight: 700, color: totalFindings > 0 ? '#f43f5e' : '#10b981' }}>{totalFindings}</Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>Scanned Files:</Typography>
              <Typography variant="caption" sx={{ fontWeight: 700 }}>{totalFiles}</Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Category Scores */}
      <Card>
        <CardContent sx={{ p: 4, display: 'flex', flexDirection: 'column', gap: 2.5 }}>
          <Typography variant="caption" sx={{ fontWeight: 700, textTransform: 'uppercase', color: 'text.secondary', letterSpacing: 1.5, mb: 1 }}>
            METRIC BREAKDOWN
          </Typography>

          {Object.entries(categoryScores).map(([cat, score]) => {
            const catColor = getScoreColor(score);
            return (
              <Box key={cat} sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="caption" sx={{ fontWeight: 600, textTransform: 'capitalize' }}>
                    {cat}
                  </Typography>
                  <Typography variant="caption" sx={{ fontWeight: 700, color: catColor }}>
                    {score}/100
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={score}
                  sx={{
                    height: 4,
                    borderRadius: 2,
                    bgcolor: 'rgba(255, 255, 255, 0.05)',
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 2,
                      bgcolor: catColor,
                    }
                  }}
                />
              </Box>
            );
          })}
        </CardContent>
      </Card>
    </Box>
  );
}
