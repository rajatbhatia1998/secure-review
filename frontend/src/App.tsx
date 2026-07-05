import { useState, useEffect } from 'react';
import { ThemeProvider, createTheme, CssBaseline, Container, Grid, Box, Typography, Card, CardContent, Alert, AlertTitle, Button } from '@mui/material';
import BarChartIcon from '@mui/icons-material/BarChart';
import ShieldIcon from '@mui/icons-material/Shield';

import Header from './components/Header';
import ConfigModal from './components/ConfigModal';
import ScanLauncher from './components/ScanLauncher';
import AgentPipeline from './components/AgentPipeline';
import Scorecard from './components/Scorecard';
import VulnerabilityExplorer from './components/VulnerabilityExplorer';
import CodeVisualizer from './components/CodeVisualizer';
import PatchRemediation from './components/PatchRemediation';

const API_BASE = 'http://localhost:8000';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#080810',
      paper: '#0f101d',
    },
    primary: {
      main: '#a855f7', // Purple
    },
    secondary: {
      main: '#06b6d4', // Cyan
    },
    text: {
      primary: '#f8fafc',
      secondary: '#94a3b8',
    },
  },
  typography: {
    fontFamily: '"Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: 'rgba(15, 16, 29, 0.6)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: 16,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            borderColor: 'rgba(168, 85, 247, 0.3)',
            boxShadow: '0 8px 30px rgba(168, 85, 247, 0.08)',
            transform: 'translateY(-2px)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
  },
});

interface LLMConfig {
  provider: string;
  base_url: string;
  model: string;
  api_key: string;
  temperature: number;
}

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

interface ReviewReport {
  report_id: string;
  repo_path: string;
  overall_score: number;
  category_scores: Record<string, number>;
  executive_summary: string;
  issues: Issue[];
  files: string[];
}

export default function App() {
  // Config & Status States
  const [repoPath, setRepoPath] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [scanStep, setScanStep] = useState<string>('idle');
  const [scanDetails, setScanDetails] = useState<string>('');
  const [report, setReport] = useState<ReviewReport | null>(null);
  const [apiHealth, setApiHealth] = useState<boolean | null>(null);
  const [llmOk, setLlmOk] = useState<boolean | null>(null);
  const [llmError, setLlmError] = useState<string>('');
  const [providers, setProviders] = useState<string[]>([]);
  const [showConfig, setShowConfig] = useState(false);
  const [saveStatus, setSaveStatus] = useState('');
  
  const [config, setConfig] = useState<LLMConfig>({
    provider: 'ollama',
    base_url: 'http://localhost:11434',
    model: 'llama3.1',
    api_key: '',
    temperature: 0.2
  });

  // Filter States
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('All');

  // File Viewer states
  const [selectedFile, setSelectedFile] = useState<string>('');
  const [fileContent, setFileContent] = useState<string>('');
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);

  useEffect(() => {
    fetchHealth();
    fetchProviders();

    const params = new URLSearchParams(window.location.search);
    const reportId = params.get('reportId');
    if (reportId) {
      loadReportById(reportId);
    }
  }, []);

  const loadReportById = async (id: string) => {
    setIsScanning(true);
    try {
      const res = await fetch(`${API_BASE}/review/${id}/status`);
      if (res.ok) {
        const data = await res.json();
        setScanStep(data.step);
        if (data.status === 'completed' && data.step === 'done') {
          setIsScanning(false);
          setReport(data.report);
          setRepoPath(data.report.repo_path);
          if (data.report.files && data.report.files.length > 0) {
            handleFileSelect(data.report.files[0], data.report.repo_path);
          }
        } else if (data.status === 'running') {
          setRepoPath(data.repo_path || '');
          pollJobStatus(id);
        } else {
          setIsScanning(false);
          setScanStep('idle');
        }
      } else {
        setIsScanning(false);
        setScanStep('idle');
      }
    } catch (e) {
      console.error('Failed to load report from URL param', e);
      setIsScanning(false);
      setScanStep('idle');
    }
  };

  const fetchHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      setApiHealth(res.ok);
    } catch {
      setApiHealth(false);
    }
  };

  const fetchProviders = async () => {
    try {
      const res = await fetch(`${API_BASE}/providers`);
      if (res.ok) {
        const data = await res.json();
        setProviders(data.available || []);
        setConfig({
          provider: data.current,
          base_url: data.base_url,
          model: data.model,
          api_key: data.api_key || '',
          temperature: 0.2
        });
        setLlmOk(data.llm_ok);
        setLlmError(data.llm_error || '');
      }
    } catch (e) {
      console.error('Failed to load LLM providers', e);
    }
  };

  const handleSaveConfig = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaveStatus('Saving...');
    try {
      const res = await fetch(`${API_BASE}/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      if (res.ok) {
        setSaveStatus('Config saved successfully!');
        fetchProviders();
        setTimeout(() => {
          setShowConfig(false);
          setSaveStatus('');
        }, 1500);
      } else {
        setSaveStatus('Failed to save configuration.');
      }
    } catch {
      setSaveStatus('Network error.');
    }
  };

  const triggerReview = async () => {
    if (!repoPath) return;
    setIsScanning(true);
    setReport(null);
    setSelectedFile('');
    setFileContent('');
    setSelectedIssue(null);
    setScanStep('scanner');
    setScanDetails('Initializing...');

    try {
      const res = await fetch(`${API_BASE}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_path: repoPath })
      });
      
      if (res.ok) {
        const jobData = await res.json();
        pollJobStatus(jobData.report_id);
      } else {
        const errorData = await res.json();
        alert(`Error: ${errorData.detail || 'Scan execution failed.'}`);
        setIsScanning(false);
        setScanStep('idle');
      }
    } catch {
      alert('Failed to connect to API backend.');
      setIsScanning(false);
      setScanStep('idle');
    }
  };

  const pollJobStatus = (reportId: string) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/review/${reportId}/status`);
        if (res.ok) {
          const data = await res.json();
          setScanStep(data.step);
          setScanDetails(data.details || '');
          
          if (data.status === 'completed' && data.step === 'done') {
            clearInterval(interval);
            setIsScanning(false);
            setReport(data.report);
            if (data.report.files && data.report.files.length > 0) {
              handleFileSelect(data.report.files[0], data.report.repo_path);
            }
          } else if (data.status === 'failed') {
            clearInterval(interval);
            setIsScanning(false);
            setScanStep('idle');
            alert(`Scan failed: ${data.error || 'Unknown error'}`);
          }
        } else {
          clearInterval(interval);
          setIsScanning(false);
          setScanStep('idle');
          alert('Error checking status.');
        }
      } catch (err) {
        clearInterval(interval);
        setIsScanning(false);
        setScanStep('idle');
      }
    }, 1500);
  };

  const handleFileSelect = async (file: string, repo: string) => {
    setSelectedFile(file);
    try {
      const res = await fetch(
        `${API_BASE}/file?repo_path=${encodeURIComponent(repo)}&file_path=${encodeURIComponent(file)}`
      );
      if (res.ok) {
        const data = await res.json();
        setFileContent(data.content);
      } else {
        setFileContent('// File contents could not be retrieved from local path.');
      }
    } catch {
      setFileContent('// Failed to connect to server to fetch file contents.');
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', pb: 8, bgcolor: 'background.default' }}>
        <Header
          provider={config.provider}
          model={config.model}
          onOpenConfig={() => setShowConfig(true)}
          hasReport={!!report}
          onNewAudit={() => { setReport(null); setRepoPath(''); setSelectedIssue(null); setSelectedFile(''); }}
          onRescan={repoPath ? triggerReview : undefined}
        />

        <Container maxWidth="xl" sx={{ mt: 5 }}>
          {llmOk === false && (
            <Alert
              severity="warning"
              variant="filled"
              action={
                <Button color="inherit" size="small" onClick={() => setShowConfig(true)}>
                  Configure
                </Button>
              }
              sx={{
                mb: 4,
                background: 'linear-gradient(135deg, #e65100 0%, #b71c1c 100%)',
                boxShadow: '0 4px 20px rgba(183, 28, 28, 0.4)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 3
              }}
            >
              <AlertTitle sx={{ fontWeight: 'bold' }}>LLM Service Connection Failed</AlertTitle>
              {llmError || 'API key is missing or invalid.'} AI-powered checks (Bug, Architecture, Dependency) will be skipped until settings are updated.
            </Alert>
          )}

          {!isScanning && !report && (
            <ScanLauncher
              repoPath={repoPath}
              setRepoPath={setRepoPath}
              isScanning={isScanning}
              onScan={triggerReview}
              apiHealth={apiHealth}
            />
          )}

          {isScanning && <AgentPipeline scanStep={scanStep} details={scanDetails} />}

          {report && (
            <Grid container spacing={4} sx={{ alignItems: 'flex-start' }}>
              {/* Left Sidebar Column */}
              <Grid size={{ xs: 12, lg: 3 }} sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                <Scorecard
                  overallScore={report.overall_score}
                  totalFindings={report.issues.length}
                  totalFiles={report.files.length}
                  categoryScores={report.category_scores}
                />

                <VulnerabilityExplorer
                  issues={report.issues}
                  selectedCategory={selectedCategory}
                  setSelectedCategory={setSelectedCategory}
                  selectedSeverity={selectedSeverity}
                  setSelectedSeverity={setSelectedSeverity}
                  selectedIssue={selectedIssue}
                  onSelectIssue={(iss) => {
                    setSelectedIssue(iss);
                    handleFileSelect(iss.file, report.repo_path);
                  }}
                />
              </Grid>

              {/* Right Content Panel Column */}
              <Grid size={{ xs: 12, lg: 9 }} sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                <Card>
                  <CardContent sx={{ p: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <BarChartIcon sx={{ color: '#06b6d4', fontSize: 20 }} />
                      <Typography variant="caption" sx={{ fontWeight: 700, textTransform: 'uppercase', color: 'text.secondary', letterSpacing: 1.5 }}>
                        AUDITOR EXECUTIVE SUMMARY
                      </Typography>
                    </Box>
                    <Typography variant="body2" sx={{ color: 'text.secondary', lineHeight: 1.7, fontSize: 13, whitespace: 'pre-wrap', whiteSpace: 'pre-wrap' }}>
                      {report.executive_summary}
                    </Typography>
                  </CardContent>
                </Card>

                {selectedIssue ? (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                    <PatchRemediation selectedIssue={selectedIssue} />
                    
                    {selectedFile && (
                      <CodeVisualizer
                        fileList={report.files}
                        issues={report.issues}
                        selectedFile={selectedFile}
                        onFileSelect={(file) => handleFileSelect(file, report.repo_path)}
                        fileContent={fileContent}
                      />
                    )}
                  </Box>
                ) : (
                  <Card sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', p: 8, gap: 2 }}>
                    <Box sx={{ p: 2, borderRadius: '50%', bgcolor: 'rgba(168, 85, 247, 0.1)', border: '1px solid rgba(168, 85, 247, 0.2)' }}>
                      <ShieldIcon sx={{ color: '#a855f7', fontSize: 32, animation: 'pulse 2s infinite ease-in-out' }} />
                    </Box>
                    <Typography variant="h6" sx={{ fontWeight: 800 }}>
                      No Vulnerability Selected
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'text.secondary', textAlign: 'center', maxWidth: 400 }}>
                      Select a warning or finding from the explorer list on the left to review the issue line-by-line and view its technical remediation recommendations.
                    </Typography>
                  </Card>
                )}
              </Grid>
            </Grid>
          )}
        </Container>
      </Box>

      {showConfig && (
        <ConfigModal
          config={config}
          setConfig={setConfig}
          providers={providers}
          saveStatus={saveStatus}
          onSave={handleSaveConfig}
          onClose={() => setShowConfig(false)}
        />
      )}
    </ThemeProvider>
  );
}
