import { google } from 'googleapis';

export default async function handler(req, res) {
  const { number } = req.query;

  if (!number) {
    return res.status(400).json({ error: 'Number parameter required' });
  }

  try {
    const auth = new google.auth.GoogleAuth({
      credentials: {
        client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
        private_key: process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
      },
      scopes: ['https://www.googleapis.com/auth/drive.readonly'],
    });

    const drive = google.drive({ version: 'v3', auth });
    
    const response = await drive.files.get({
      fileId: process.env.GOOGLE_DRIVE_FILE_ID,
      alt: 'media',
    });

    // ✅ DEBUG: Response check karo
    console.log('Response type:', typeof response.data);
    console.log('Response data:', response.data);
    
    // Try different parsing methods
    let database;
    if (typeof response.data === 'string') {
      database = JSON.parse(response.data);
    } else {
      database = response.data;
    }

    console.log('Database type:', typeof database);
    
    if (!Array.isArray(database)) {
      return res.status(500).json({ 
        error: 'Database format invalid',
        receivedType: typeof database
      });
    }

    const result = database.find(item => item.mobile === number);

    if (!result) {
      return res.status(404).json({ error: 'Number not found' });
    }

    res.status(200).json(result);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal server error: ' + error.message });
  }
}
