import React, { useEffect, useState } from 'react';
import { 
    Typography, 
    Paper, 
    Grid, 
    Button, 
    Checkbox, 
    FormControlLabel, 
    FormControl, 
    Box,
    Divider,
    Chip
} from '@mui/material';
import { ArrowBack, PlayArrow, Description } from '@mui/icons-material';
import { createWorkflow, fetchAvailableWorkflows } from '../util/workflowsClient';
import { useFormContext } from './context';

const FormWorkflowsContainer = () => {
    const { record, remoteFiles } = useFormContext();
    const recordId = record.id;
    
    const [availableWorkflows, setAvailableWorkflows] = useState([]); 
    const [currentView, setCurrentView] = useState('workflows'); // 'workflows' | 'files'
    const [selectedWorkflow, setSelectedWorkflow] = useState(null);
    const [selectedFiles, setSelectedFiles] = useState([]);
    
    useEffect(() => {
        const fetchWorkflows = async () => {
            const response = await fetchAvailableWorkflows(remoteFiles);
            if (response.ok) {
                setAvailableWorkflows(response.data.workflows);
            }
        };
        
        fetchWorkflows();
    }, [remoteFiles]);

    const handleWorkflowSelect = (workflow) => {
        setSelectedWorkflow(workflow);
        setSelectedFiles([]); // Reset file selection
        setCurrentView('files');
    };

    const handleBackToWorkflows = () => {
        setCurrentView('workflows');
        setSelectedWorkflow(null);
        setSelectedFiles([]);
    };

    const handleFileToggle = (file) => {
        setSelectedFiles(prev => {
            if (prev.includes(file)) {
                return prev.filter(f => f !== file);
            } else {
                return [...prev, file];
            }
        });
    };

    const handleRunWorkflow = () => {

        if (selectedWorkflow && selectedFiles.length > 0) {
            createWorkflow(record.id, selectedWorkflow.name, remoteFiles.filter((file) => selectedFiles.includes(file.key))); 
        }
    };

    // Render workflow list view
    const renderWorkflowList = () => (
        <>
            <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
                Available Workflows
            </Typography>
            <Grid container spacing={2} direction="column">
                {availableWorkflows.map((workflow, index) => (
                    <Grid item xs={12} key={index}>
                        <Paper 
                            elevation={1} 
                            sx={{ 
                                p: 2, 
                                cursor: 'pointer',
                                transition: 'all 0.2s ease-in-out',
                                '&:hover': {
                                    elevation: 3,
                                    backgroundColor: 'action.hover'
                                }
                            }}
                            onClick={() => handleWorkflowSelect(workflow)}
                        >
                            <Box display="flex" alignItems="center" justifyContent="space-between">
                                <Box>
                                    <Typography variant="h6" component="div">
                                        {workflow.name}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                        {workflow.mimetype}
                                    </Typography>
                                    <Box sx={{ mt: 1 }}>
                                        <Chip 
                                            size="small" 
                                            label={`${workflow.files.length} file${workflow.files.length !== 1 ? 's' : ''}`} 
                                            variant="outlined"
                                        />
                                    </Box>
                                </Box>
                                <PlayArrow color="primary" />
                            </Box>
                        </Paper>
                    </Grid>
                ))}
            </Grid>
        </>
    );

    // Render file selection view
    const renderFileSelection = () => (
        <>
            <Box display="flex" alignItems="center" sx={{ mb: 3 }}>
                <Button
                    startIcon={<ArrowBack />}
                    onClick={handleBackToWorkflows}
                    sx={{ mr: 2 }}
                >
                    Back to Workflows
                </Button>
                <Box>
                    <Typography variant="h6" component="div">
                        {selectedWorkflow?.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        {selectedWorkflow?.mimetype}
                    </Typography>
                </Box>
            </Box>

            <Divider sx={{ mb: 3 }} />

            <Box display="flex" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
                <Typography variant="subtitle1">
                    Select files to process:
                </Typography>
                {selectedFiles.length > 0 && (
                    <Chip 
                        size="small" 
                        label={`${selectedFiles.length} selected`} 
                        color="primary"
                        variant="outlined"
                    />
                )}
            </Box>

            <FormControl component="fieldset" sx={{ width: '100%' }}>
                <Grid container spacing={1} direction="column">
                    {selectedWorkflow?.files.map((file, index) => (
                        <Grid item xs={12} key={index}>
                            <Paper 
                                elevation={1} 
                                sx={{ 
                                    p: 2,
                                    backgroundColor: selectedFiles.includes(file) ? 'action.selected' : 'background.paper',
                                    cursor: 'pointer',
                                    transition: 'background-color 0.2s ease-in-out',
                                    '&:hover': {
                                        backgroundColor: selectedFiles.includes(file) ? 'action.selected' : 'action.hover'
                                    }
                                }}
                                onClick={() => handleFileToggle(file)}
                            >
                                <FormControlLabel
                                    control={
                                        <Checkbox 
                                            checked={selectedFiles.includes(file)}
                                            onChange={(e) => e.stopPropagation()}
                                        />
                                    }
                                    label={
                                        <Box display="flex" alignItems="center">
                                            <Description sx={{ mr: 1, color: 'text.secondary' }} />
                                            <Typography variant="body1">
                                                {file}
                                            </Typography>
                                        </Box>
                                    }
                                    sx={{ margin: 0, width: '100%' }}
                                />
                            </Paper>
                        </Grid>
                    ))}
                </Grid>
            </FormControl>

            {selectedFiles.length > 0 && (
                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
                    <Button
                        variant="contained"
                        startIcon={<PlayArrow />}
                        onClick={handleRunWorkflow}
                        size="large"
                    >
                        Run Workflow ({selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''})
                    </Button>
                </Box>
            )}
        </>
    );

    return (
        <Paper elevation={3} sx={{ p: 3 }}>
            {currentView === 'workflows' ? renderWorkflowList() : renderFileSelection()}
        </Paper>
    );
};

export default FormWorkflowsContainer;
