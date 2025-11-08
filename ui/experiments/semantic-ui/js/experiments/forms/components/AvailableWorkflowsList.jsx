import React from 'react';
import {
    Typography,
    Paper,
    Chip,
    Stack,
    Button
} from '@mui/material';
import { PlayArrow } from '@mui/icons-material';

const handleWorkflowSelect = (onWorkflowSelect) =>
    (workflow) => {
        onWorkflowSelect(workflow);
    };

const AvailableWorkflowsList = ({ workflows, onWorkflowSelect }) => {

    return (
        <Stack spacing={3}>
            <Typography variant="h6" gutterBottom>
                Available Workflows
            </Typography>
            <Stack spacing={2}>
                {workflows.map((workflow, index) => (
                    <Paper key={index} elevation={1}>
                        <Button
                            onClick={() => handleWorkflowSelect(onWorkflowSelect)(workflow)}
                            fullWidth
                            sx={{ textTransform: 'none', p: 2 }}
                        >
                            <Stack direction="row" justifyContent="space-between" alignItems="center" width="100%">
                                <Stack spacing={1} alignItems="flex-start">
                                    <Typography variant="h6" component="div" color="text.primary">
                                        {workflow.name}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        {workflow.mimetype}
                                    </Typography>
                                    <Chip
                                        size="small"
                                        label={`${workflow.files.length} file${workflow.files.length !== 1 ? 's' : ''}`}
                                    />
                                </Stack>
                                <PlayArrow color="primary" />
                            </Stack>
                        </Button>
                    </Paper>
                ))}
            </Stack>
        </Stack>
    );
};

export default AvailableWorkflowsList;
