import logging
import os
from optparse import OptionParser

import baseutils
from orchutils import vault


logger = logging.getLogger()


def upload_files(files_dir, vault_path, debug):
    """
    Uploads files to Vault. All files in the passed directory are uploaded.
    They are uploaded as text content at the path "{vault_path}/<filename>" and sub-key "content".
    Args:
        files_dir: The directory to upload files from
        vault_path: The path in Vault to upload files to
    """
    file_names = os.listdir(files_dir)
    for file_name in file_names:
        upload_path = '{parent}/{file}'.format(parent=vault_path, file=file_name)
        if debug:
            logger.info('Will not upload {file} to {upload_path}'.format(file=file_name, upload_path=upload_path))
        else:
            logger.info('Uploading {file} to {upload_path}'.format(file=file_name, upload_path=upload_path))
            with open(os.path.join(files_dir, file_name), 'r') as fh:
                vault.write(upload_path, {'content': fh.read()})


def main():
    baseutils.configure_logger(logger, stream=True)
    parser = OptionParser()
    parser.add_option('--files-dir', dest='files_dir', help='The directory containing the text files. If the names already exist in Vault, they will be overwritten')
    parser.add_option('--upload-path', dest='upload_path', default='secret/ansible/sos/iks/ovpn/files', help='The Vault path to upload the files to (Optional, default: %default)')
    parser.add_option('--vault-url', dest='vault_url', default='https://vaulty.sjc03.dc.local:8200', help='The Vault server upload the files to (Optional, default: %default)')
    parser.add_option('--vault-token', dest='vault_token', help='The token for authenticating with Vault')
    parser.add_option('-d', '--debug', dest='debug', action='store_true', help='Lists the files to upload and authenticates with vault but does not upload any files')
    (options, args) = parser.parse_args()

    if not options.files_dir:
        raise Exception('Command line argument --files-dir not provided.  Execute -h for usage')
    if not options.vault_token:
        raise Exception('Command line argument --vault-token not provided.  Execute -h for usage')

    vault.login(options.vault_url, options.vault_token)
    upload_files(options.files_dir, options.upload_path, options.debug)


if __name__ == '__main__':
    main()
