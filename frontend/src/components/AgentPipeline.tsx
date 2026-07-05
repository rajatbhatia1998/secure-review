import { Paper, Typography, Box, LinearProgress } from '@mui/material';
import ActivityIcon from '@mui/icons-material/Animation';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import RadarIcon from '@mui/icons-material/Radar';

interface AgentPipelineProps {
  scanStep: string;
  details?: string;
}

export default function AgentPipeline({ scanStep, details }: AgentPipelineProps) {
  const steps = [
    { name: 'Scanner', key: 'scanner', desc: 'Mapping Repo' },
    { name: 'SAST Tools', key: 'sast', desc: 'Heuristics Audit' },
    { name: 'Planner', key: 'planner', desc: 'Workload Planning' },
    { name: 'Agents', key: 'agents', desc: 'Parallel Scans' },
    { name: 'Summary', key: 'summary', desc: 'Compiling Score' }
  ];

  const activeIndex = steps.map(s => s.key).indexOf(scanStep);

  return (
    <Paper sx={{ p: 5, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, borderRadius: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <RadarIcon sx={{ color: '#a855f7', animation: 'spin 4s linear infinite' }} />
        <Typography variant="subtitle2" sx={{ fontWeight: 700, textTransform: 'uppercase', color: '#a855f7', letterSpacing: 1.5 }}>
          LANGGRAPH WORKFLOW NODE PROGRESSION
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'center', gap: { xs: 2, lg: 3 }, width: '100%', py: 2 }}>
        {steps.map((step, idx) => {
          const isActive = scanStep === step.key;
          const isCompleted = idx < activeIndex;
          
          return (
            <Box key={step.key} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Box
                sx={{
                  p: 3,
                  width: 140,
                  borderRadius: 3,
                  border: '1px solid',
                  borderColor: isActive ? '#a855f7' : (isCompleted ? 'rgba(16, 185, 129, 0.3)' : 'rgba(255, 255, 255, 0.05)'),
                  bgcolor: isActive ? 'rgba(168, 85, 247, 0.06)' : (isCompleted ? 'rgba(16, 185, 129, 0.02)' : 'rgba(255, 255, 255, 0.01)'),
                  textAlign: 'center',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  transition: 'all 0.3s',
                  boxShadow: isActive ? '0 0 20px rgba(168, 85, 247, 0.2)' : 'none',
                  opacity: isActive || isCompleted ? 1 : 0.4
                }}
              >
                {isCompleted ? (
                  <CheckCircleIcon sx={{ color: '#10b981', mb: 1 }} />
                ) : (
                  <ActivityIcon sx={{ color: isActive ? '#a855f7' : 'text.secondary', mb: 1, animation: isActive ? 'pulse 1s infinite' : 'none' }} />
                )}
                <Typography variant="body2" sx={{ fontWeight: 700, color: isActive ? '#a855f7' : 'text.primary' }}>
                  {step.name}
                </Typography>
                <Typography variant="caption" sx={{ color: 'text.secondary', mt: 0.5, fontSize: 10 }}>
                  {step.desc}
                </Typography>
              </Box>
              
              {idx < steps.length - 1 && (
                <ArrowForwardIcon sx={{ color: isCompleted ? '#10b981' : 'rgba(255, 255, 255, 0.1)', fontSize: 18 }} />
              )}
            </Box>
          );
        })}
      </Box>

      <Box sx={{ width: '100%', maxWidth: 500, mt: 2 }}>
        <LinearProgress
          variant="determinate"
          value={((activeIndex + 1) / steps.length) * 100}
          color="primary"
          sx={{
            height: 6,
            borderRadius: 3,
            bgcolor: 'rgba(255, 255, 255, 0.05)',
            '& .MuiLinearProgress-bar': {
              borderRadius: 3,
              background: 'linear-gradient(90deg, #a855f7, #06b6d4)',
            }
          }}
        />
      </Box>

      {details && (
        <Box
          sx={{
            mt: 1,
            p: 2,
            width: '100%',
            maxWidth: 500,
            textAlign: 'center',
            bgcolor: 'rgba(255, 255, 255, 0.02)',
            border: '1px dashed rgba(168, 85, 247, 0.2)',
            borderRadius: 2
          }}
        >
          <Typography variant="body2" color="text.secondary" sx={{ fontFamily: 'monospace', fontStyle: 'italic', fontSize: '0.85rem' }}>
            {details}
          </Typography>
        </Box>
      )}
    </Paper>
  );
}
