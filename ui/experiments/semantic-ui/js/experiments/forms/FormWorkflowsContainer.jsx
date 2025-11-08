import React, { useState, useEffect } from 'react';
import {
    Paper,
    Tabs,
    Tab
} from '@mui/material';
import { useFormContext } from './context';
import { fetchAvailableWorkflows } from '../util/workflowsClient';
import AvailableWorkflowsList from './components/AvailableWorkflowsList';
import FileSelection from './components/FileSelection';
import ActiveWorkflowsList from './components/ActiveWorkflowsList';
import ActiveWorkflowDetail from './components/ActiveWorkflowDetail';

const handleTabChange = (setCurrentTab, setCurrentView, setActiveView) =>
    (_, newValue) => {
        setCurrentTab(newValue);
        setCurrentView('workflows');
        setActiveView('list');
    };

const FormWorkflowsContainer = () => {
    const { record, remoteFiles } = useFormContext();
    const recordId = record.id;

    const [workflowsEnabled, setWorkflowsEnabled] = useState(true);
    const [availableWorkflowsAccessible, setAvailableWorkflowsAccessible] = useState(true);
    const [availableWorkflows, setAvailableWorkflows] = useState([]);
    const [currentTab, setCurrentTab] = useState(0);
    const [currentView, setCurrentView] = useState('workflows'); // 'workflows' | 'files'
    const [activeView, setActiveView] = useState('list'); // 'list' | 'detail'
    const [selectedWorkflow, setSelectedWorkflow] = useState(null);
    const [selectedActiveWorkflow, setSelectedActiveWorkflow] = useState(null);

    const handleWorkflowSelect = (workflow) => {
        setSelectedWorkflow(workflow);
        setCurrentView('files');
    };

    const handleBackToWorkflows = () => {
        setCurrentView('workflows');
        setSelectedWorkflow(null);
    };

    const handleWorkflowRun = () => {
        setCurrentView('workflows');
        setCurrentTab(1);
    };

    const handleActiveWorkflowSelect = (workflow) => {
        setSelectedActiveWorkflow(workflow);
        setActiveView('detail');
    };

    const handleBackToActiveList = () => {
        setActiveView('list');
        setSelectedActiveWorkflow(null);
    };

    useEffect(() => {
        const fetchWorkflows = async () => {
            const response = await fetchAvailableWorkflows(recordId, remoteFiles);
            if (response.ok) {
                setWorkflowsEnabled(true);
                setAvailableWorkflows(response.data.workflows);
            } else if (response.status === 403) {
                setWorkflowsEnabled(true);
                setAvailableWorkflowsAccessible(false);
                setAvailableWorkflows([]);
            } else {
                setWorkflowsEnabled(false);
                setAvailableWorkflows([]);
            }
        };

        fetchWorkflows();
    }, [remoteFiles]);

    if (!workflowsEnabled) {
        return <></>;
    }

    return (
        <Paper elevation={3} sx={{ p: 3 }}>
            <Tabs variant="fullWidth" value={currentTab} onChange={handleTabChange(setCurrentTab, setCurrentView, setActiveView)} sx={{ mb: 3 }}>
                {availableWorkflowsAccessible && <Tab label="Available Workflows" />}
                <Tab label="Active Workflows" />
            </Tabs>

            {availableWorkflowsAccessible && currentTab === 0 && (
                <>
                    {currentView === 'workflows' ? (
                        <AvailableWorkflowsList
                            workflows={availableWorkflows}
                            onWorkflowSelect={handleWorkflowSelect}
                        />
                    ) : (
                        <FileSelection
                            selectedWorkflow={selectedWorkflow}
                            remoteFiles={remoteFiles}
                            recordId={recordId}
                            onBack={handleBackToWorkflows}
                            onWorkflowRun={handleWorkflowRun}
                        />
                    )}
                </>
            )}

            {(!availableWorkflowsAccessible || currentTab === 1) && (
                <>
                    {activeView === 'list' ? (
                        <ActiveWorkflowsList
                            recordId={recordId}
                            onWorkflowSelect={handleActiveWorkflowSelect}
                        />
                    ) : (
                        <ActiveWorkflowDetail
                            recordId={recordId}
                            selectedActiveWorkflow={selectedActiveWorkflow}
                            onBack={handleBackToActiveList}
                        />
                    )}
                </>
            )}
        </Paper>
    );
};

export default FormWorkflowsContainer;
