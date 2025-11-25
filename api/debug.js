import { google } from 'googleapis';

export default async function handler(req, res) {
  try {
    const auth = new google.auth.GoogleAuth({
      credentials: {
        client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
        private_key: process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
      },
      scopes: ['https://www.googleapis.com/auth/drive.readonly'],
    });

    const drive = google.drive({ version: 'v3', auth });
    
    // File 1 check karo
    const response1 = await drive.files.get({
      fileId: process.env.GOOGLE_DRIVE_FILE_ID_1,
      alt: 'media',
    });

    const csvText1 = response1.data;
    const lines1 = csvText1.split('\n');
    
    res.status(200).json({
      file1_first_line: lines1[0],
      file1_total_lines: lines1.length,
      file1_sample: lines1.slice(0, 3) // First 3 lines
    });

  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Debug error: ' + error.message });
  }
}
