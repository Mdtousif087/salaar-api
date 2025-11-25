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
    
    // Just file metadata check karo
    const fileInfo = await drive.files.get({
      fileId: process.env.GOOGLE_DRIVE_FILE_ID_1,
      fields: 'name,size,mimeType,shared'
    });

    res.status(200).json({
      message: 'File access successful',
      file_info: fileInfo.data
    });

  } catch (error) {
    res.status(500).json({ 
      error: 'File access failed',
      details: error.message 
    });
  }
}
