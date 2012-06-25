package info.caq9;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;

import weibo4j.Timeline;
import weibo4j.Weibo;
import weibo4j.http.ImageItem;
import weibo4j.model.WeiboException;

public class UploadPic {
	// Returns the contents of the file in a byte array.
	public static byte[] getBytesFromFile(File file) throws IOException {
		InputStream is = new FileInputStream(file);

		// Get the size of the file
		long length = file.length();

		// You cannot create an array using a long type.
		// It needs to be an int type.
		// Before converting to an int type, check
		// to ensure that file is not larger than Integer.MAX_VALUE.
		if (length > Integer.MAX_VALUE) {
			// File is too large
		}

		// Create the byte array to hold the data
		byte[] bytes = new byte[(int) length];

		// Read in the bytes
		int offset = 0;
		int numRead = 0;
		while (offset < bytes.length
				&& (numRead = is.read(bytes, offset, bytes.length - offset)) >= 0) {
			offset += numRead;
		}

		// Ensure all the bytes have been read in
		if (offset < bytes.length) {
			throw new IOException("Could not completely read file "
					+ file.getName());
		}

		// Close the input stream and return bytes
		is.close();
		return bytes;
	}

	/**
	 * @param args
	 *            : [access token] [text] [pic filename]
	 */
	public static void main(String[] args) throws Exception {
		String access_token = args[0];
		Weibo weibo = new Weibo();
		weibo.setToken(access_token);
		Timeline tl = new Timeline();
		//BufferedReader br = new BufferedReader(new FileReader(args[1]));
		String text = args[1];
		//String line;
		//while ((line = br.readLine()) != null)
		//	text += line;
		//br.close();
		System.out.println(text);

		try {
			tl.UploadStatus(text, new ImageItem(getBytesFromFile(new File(
					args[2]))));
		} catch (WeiboException e) {
			e.printStackTrace();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}