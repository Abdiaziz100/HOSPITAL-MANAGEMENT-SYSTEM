import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Payment as PaymentIcon,
  Receipt as ReceiptIcon,
  Print as PrintIcon,
  Add as AddIcon,
  AttachMoney as MoneyIcon
} from '@mui/icons-material';
import axios from 'axios';
import { useNotification } from '../contexts/NotificationContext';


const BillingManagement = () => {
  const [bills, setBills] = useState([]);
  const [patients, setPatients] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [openPaymentDialog, setOpenPaymentDialog] = useState(false);
  const [selectedBill, setSelectedBill] = useState(null);
  const [formData, setFormData] = useState({
    patient_id: '',
    total_amount: '',
    due_date: '',
    items: [{ service_code: '', description: '', quantity: 1, unit_price: '' }]
  });
  const [paymentData, setPaymentData] = useState({
    amount: '',
    payment_method: 'cash',
    reference_number: '',
    notes: ''
  });
const { showSuccess, showError } = useNotification();

  useEffect(() => {
const loadData = async () => {
      try {
        const [billsRes, patientsRes] = await Promise.all([
          axios.get('/api/bills'),
          axios.get('/api/patients')
        ]);
        setBills(billsRes.data.bills || []);
        setPatients(patientsRes.data || []);
      } catch (error) {
        console.error('Failed to load billing data:', error);
        showError('Failed to load billing data');
      }
    };
    loadData();
    }, [showError]);

  const handleCreateBill = async (e) => {
    e.preventDefault();
    try {
await axios.post('/api/bills', formData);
      showSuccess('Bill created successfully');
      setOpenDialog(false);
      // Refresh data
      window.location.reload();
    } catch (error) {
      showError('Failed to create bill');
      console.error(error);
    }
  };

  const handleProcessPayment = async (e) => {
    e.preventDefault();
    try {
await axios.post(`/api/bills/${selectedBill.id}/payment`, paymentData);
      showSuccess('Payment processed successfully');
      setOpenPaymentDialog(false);
      window.location.reload();
    } catch (error) {
      showError('Failed to process payment');
    }
  };

  // eslint-disable-next-line no-unused-vars
  const resetForm = () => {
    setFormData({
      patient_id: '',
      total_amount: '',
      due_date: '',
      items: [{ service_code: '', description: '', quantity: 1, unit_price: '' }]
    });
  };

  const addBillItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { service_code: '', description: '', quantity: 1, unit_price: '' }]
    });
  };

  const updateBillItem = (index, field, value) => {
    const updatedItems = formData.items.map((item, i) => 
      i === index ? { ...item, [field]: value } : item
    );
    setFormData({ ...formData, items: updatedItems });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'paid': return 'success';
      case 'pending': return 'warning';
      case 'overdue': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Billing Management</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Create Bill
        </Button>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <MoneyIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Revenue
                  </Typography>
                  <Typography variant="h5">
                    ${bills.reduce((sum, bill) => sum + bill.total_amount, 0).toFixed(2)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <PaymentIcon color="success" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Collected
                  </Typography>
                  <Typography variant="h5">
                    ${bills.reduce((sum, bill) => sum + bill.paid_amount, 0).toFixed(2)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <ReceiptIcon color="warning" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Outstanding
                  </Typography>
                  <Typography variant="h5">
                    ${bills.reduce((sum, bill) => sum + (bill.total_amount - bill.paid_amount), 0).toFixed(2)}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Typography variant="h2" color="primary" sx={{ mr: 2 }}>
                  {bills.length}
                </Typography>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Bills
                  </Typography>
                  <Typography variant="body2">
                    {bills.filter(b => b.status === 'paid').length} Paid
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Bills Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Bill Number</TableCell>
              <TableCell>Patient</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Paid</TableCell>
              <TableCell>Balance</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Due Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {bills.map((bill) => (
              <TableRow key={bill.id}>
                <TableCell>{bill.bill_number}</TableCell>
                <TableCell>{bill.patient_name}</TableCell>
                <TableCell>${bill.total_amount.toFixed(2)}</TableCell>
                <TableCell>${bill.paid_amount.toFixed(2)}</TableCell>
                <TableCell>${bill.balance.toFixed(2)}</TableCell>
                <TableCell>
                  <Chip
                    label={bill.status}
                    color={getStatusColor(bill.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{new Date(bill.due_date).toLocaleDateString()}</TableCell>
                <TableCell>
                  {bill.balance > 0 && (
                    <Tooltip title="Process Payment">
                      <IconButton
                        onClick={() => {
                          setSelectedBill(bill);
                          setOpenPaymentDialog(true);
                        }}
                      >
                        <PaymentIcon />
                      </IconButton>
                    </Tooltip>
                  )}
                  <Tooltip title="Print Bill">
                    <IconButton>
                      <PrintIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create Bill Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Bill</DialogTitle>
        <form onSubmit={handleCreateBill}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel>Patient</InputLabel>
                  <Select
                    value={formData.patient_id}
                    onChange={(e) => setFormData({...formData, patient_id: e.target.value})}
                  >
                    {patients.map((patient) => (
                      <MenuItem key={patient.id} value={patient.id}>
                        {`${patient.first_name} ${patient.last_name}`}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Due Date"
                  type="date"
                  value={formData.due_date}
                  onChange={(e) => setFormData({...formData, due_date: e.target.value})}
                  InputLabelProps={{ shrink: true }}
                  required
                />
              </Grid>
              
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Bill Items
                </Typography>
                {formData.items.map((item, index) => (
                  <Grid container spacing={2} key={index} sx={{ mb: 2 }}>
                    <Grid item xs={3}>
                      <TextField
                        fullWidth
                        label="Service Code"
                        value={item.service_code}
                        onChange={(e) => updateBillItem(index, 'service_code', e.target.value)}
                        required
                      />
                    </Grid>
                    <Grid item xs={4}>
                      <TextField
                        fullWidth
                        label="Description"
                        value={item.description}
                        onChange={(e) => updateBillItem(index, 'description', e.target.value)}
                        required
                      />
                    </Grid>
                    <Grid item xs={2}>
                      <TextField
                        fullWidth
                        label="Quantity"
                        type="number"
                        value={item.quantity}
                        onChange={(e) => updateBillItem(index, 'quantity', parseInt(e.target.value))}
                        required
                      />
                    </Grid>
                    <Grid item xs={3}>
                      <TextField
                        fullWidth
                        label="Unit Price"
                        type="number"
                        step="0.01"
                        value={item.unit_price}
                        onChange={(e) => updateBillItem(index, 'unit_price', parseFloat(e.target.value))}
                        required
                      />
                    </Grid>
                  </Grid>
                ))}
                <Button onClick={addBillItem} variant="outlined" size="small">
                  Add Item
                </Button>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Total Amount"
                  type="number"
                  step="0.01"
                  value={formData.total_amount}
                  onChange={(e) => setFormData({...formData, total_amount: e.target.value})}
                  required
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Create Bill</Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Payment Dialog */}
      <Dialog open={openPaymentDialog} onClose={() => setOpenPaymentDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Process Payment</DialogTitle>
        <form onSubmit={handleProcessPayment}>
          <DialogContent>
            {selectedBill && (
              <Box mb={2}>
                <Typography variant="body2" color="textSecondary">
                  Bill: {selectedBill.bill_number}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Outstanding: ${selectedBill.balance.toFixed(2)}
                </Typography>
              </Box>
            )}
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Payment Amount"
                  type="number"
                  step="0.01"
                  value={paymentData.amount}
                  onChange={(e) => setPaymentData({...paymentData, amount: e.target.value})}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel>Payment Method</InputLabel>
                  <Select
                    value={paymentData.payment_method}
                    onChange={(e) => setPaymentData({...paymentData, payment_method: e.target.value})}
                  >
                    <MenuItem value="cash">Cash</MenuItem>
                    <MenuItem value="card">Card</MenuItem>
                    <MenuItem value="check">Check</MenuItem>
                    <MenuItem value="insurance">Insurance</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Reference Number"
                  value={paymentData.reference_number}
                  onChange={(e) => setPaymentData({...paymentData, reference_number: e.target.value})}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Notes"
                  multiline
                  rows={2}
                  value={paymentData.notes}
                  onChange={(e) => setPaymentData({...paymentData, notes: e.target.value})}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenPaymentDialog(false)}>Cancel</Button>
            <Button type="submit" variant="contained">Process Payment</Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default BillingManagement;
