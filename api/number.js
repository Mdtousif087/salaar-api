import { google } from 'googleapis';

export default async function handler(req, res) {
  const { number } = req.query;

  if (!number) {
    return res.status(400).json({ error: 'Number parameter required' });
  }

  try {
    console.log('API called with number:', number);
    
    const auth = new google.auth.GoogleAuth({
      credentials: {
        client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
        private_key: process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
      },
      scopes: ['https://www.googleapis.com/auth/drive.readonly'],
    });

    const drive = google.drive({ version: 'v3', auth });
    
    console.log('Reading file 1...');
    const response1 = await drive.files.get({
      fileId: process.env.GOOGLE_DRIVE_FILE_ID_1,
      alt: 'media',
    });

    console.log('File 1 content received');
    const csvText = response1.data;
    console.log('CSV length:', csvText.length);
    
    // Simple CSV parsing
    const lines = csvText.split('\n').filter(line => line.trim());
    console.log('Total lines:', lines.length);
    
    if (lines.length === 0) {
      return res.status(200).json({ message: 'File is empty', lines: 0 });
    }

    const headers = lines[0].split(',').map(h => h.trim());
    console.log('Headers:', headers);

    // Just return first few lines for testing
    const sampleData = lines.slice(0, 5).map(line => {
      const values = line.split(',');
      const record = {};
      headers.forEach((header, index) => {
        record[header] = values[index] ? values[index].trim() : '';
      });
      return record;
    });

    res.status(200).json({
      message: 'API working - sample data',
      search_number: number,
      sample_data: sampleData,
      total_lines: lines.length
    });

  } catch (error) {
    console.error('Full error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      message: error.message,
      stack: error.stack
    });
  }
}
