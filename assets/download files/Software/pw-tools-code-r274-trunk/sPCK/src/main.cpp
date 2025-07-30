#include "main.h"

void print_help()
{
    printf("Usage: spck MODE OPTION [COMPRESSION]\n");
    printf("\n");
    printf("MODE:\n");
    printf("\n");
    printf("  -pw             Perfect World\n");
    printf("  -jd             Jade Dynasty\n");
    printf("  -fw             Forsaken World\n");
    printf("  -eso            Ether Sage\n");
    printf("  -rwpd           Steps / Sincerity Dance Scrambling\n");
    printf("\n");
    printf("OPTION:\n");
    printf("\n");
    printf("  -x FILE         Extract a *.pck FILE\n");
    printf("                  Files will be extracted into a subdirectory\n");
    printf("                  of the same directory\n");
    printf("  -xp FILE        Extract and decode a *.cup patch FILE\n");
    printf("                  Files will be decoded into a subdirectory\n");
    printf("                  of the same directory\n");
    printf("  -c DIRECTORY    Compress content of DIRECTORY to *.pck\n");
    printf("                  File will be created in the same directory\n");
    printf("  -cp DIRECTORY   Compress content of DIRECTORY to *.xup\n");
    printf("                  File will be created in the same directory\n");
    printf("                  !!! ONLY SUPPORTED ON WINDOWS !!!\n");
    printf("  -a DIRECTORY    Insert content from DIRECTORY to the\n");
    printf("                  corresponding *.pck file\n");
    printf("  -ap DIRECTORY   Insert content from DIRECTORY to the\n");
    printf("                  corresponding *.pck file\n");
    printf("                  The names of files and subdirectories\n");
    printf("                  in DIRECTORY must be base64 encoded\n");
    printf("\n");
    printf("COMPRESSION (Optional):\n");
    printf("\n");
    printf("  VALUE           Number VALUE indicating compression level\n");
    printf("                  Range [0..9] with 0: none, 9: maximum\n");
    printf("                  This is optional, default value: 1\n");
    printf("                  Only affects compress/insert mode\n");
    printf("\n");
    printf("Further information can be found at:\n");
    printf("http://sourceforge.net/p/pw-tools/doc/sPCK\n");
}

bool compare(wxByte* buffer1, wxByte* buffer2, wxUint32 length)
{
    for(wxUint32 i=0; i<length; i++)
    {
        if(buffer1[i]!=buffer2[i])
        {
            return false;
        }
    }
    return true;
}

/*
    delete directory recursive
*/
void wxDeldir(wxString Directory)
{
    wxArrayString files;

    wxDirTraverserFiles fileTraverser(files);
    wxDir(Directory).Traverse(fileTraverser);

    for(wxUint32 i=0; i<files.Count(); i++)
    {
        wxRemoveFile(files[i]);
    }

    files.Clear();

    wxDirTraverserDirectories dirTraverser(files);
    wxDir(Directory).Traverse(dirTraverser);
    // Reverse Sort to make sure first delte folders without subfolders
    files.Sort(true);

    for(wxUint32 i=0; i<files.Count(); i++)
    {
        wxRmdir(files[i]);
    }

    wxRmdir(Directory);
}

wxByte* fillPath(wxByte* source)
{
    wxByte* target = new wxByte[260];

    bool end = false;

    for(wxUint32 i=0; i<260; i++)
    {
        if(!end && source[i]==0)
        {
            end = true;
        }
        if(end)
        {
            target[i] = 0;
        }
        else
        {
            target[i] = source[i];
        }
    }

    return target;
}

wxByte* deflate(wxByte* buffer, wxUint32 sizeCompressed, wxUint32 sizeDecompressed)
{
    wxByte* out = new wxByte[sizeDecompressed];
    wxMemoryInputStream mis(buffer, sizeCompressed);
    wxZlibInputStream* zis = new wxZlibInputStream(mis);
    zis->Read(out, sizeDecompressed);
    wxDELETE(zis);
    return out;
}

wxByte* inflate(wxByte* buffer, wxUint32 sizeDecompressed, wxUint32& sizeCompressed, wxUint32 compressionLevel)
{
    wxMemoryOutputStream mos;
    wxZlibOutputStream* zos = new wxZlibOutputStream(mos, compressionLevel);
    zos->Write(buffer, sizeDecompressed);
    wxDELETE(zos);
    sizeCompressed = mos.GetSize();
    wxByte* out = new wxByte[sizeCompressed];
    mos.CopyTo(out, sizeCompressed);
    return out;
}

/*
 * Extract a part from an input stream and write it to the output stream
 *
 * @param[in] fis
 * @param[in] fileOut
 * @param[in] posStart
 * @param[in] posEnd The byte at the end poition will be excluded
 *
 * @return
 */
bool segmentation(wxFFileInputStream* fis, wxString fileOut, size_t posStart, size_t posEnd) {
    if(posStart < 0 || posEnd < 0 || posStart >= posEnd || posEnd > fis->GetSize()) {
        return false;
    }
    size_t bufferSize = 8*1024*1024; // 8 MB
    wxByte* buffer = new wxByte[bufferSize];
    // goto start position
    fis->SeekI(posStart);

    // open output file
    wxFFileOutputStream fos(fileOut);
    while((size_t)fis->TellI() < posEnd) {
        if(posEnd - fis->TellI() < bufferSize) {
            bufferSize = (size_t)(posEnd - fis->TellI());
        }
        fis->Read(buffer, bufferSize);
        fos.Write(buffer, bufferSize);
    }

    // close segment
    fos.Close();
    wxDELETEA(buffer);

    return true;
}

/*
 * Copy a pck and pkx file to a merged file (keeps the original pck and pkx)
 *
 * @param[in] fileIn Path to the pck file
 *
 * @return
 */
void mergePCK(wxString fileIn) {
    // FIXME: check if fileIn ends with .pck and not .pckx
    //wxPrintf(wxT("Operation Mode: Merge PCK + PKX Files\n\n");

    wxString filePCK = fileIn;
    wxString filePKX = fileIn.BeforeLast('.') + wxT(".pkx");
    wxString filePCKX = fileIn.BeforeLast('.') + wxT(".pckx");
    // check if fileIn has a corresponding pkx file
    if(!wxFile::Exists(filePKX)) {
        wxPrintf(wxT("Nothing to be done\n"));
        return;
    }

    wxPrintf(wxT("Merging: .pck + .pkx => .pckx\n"));
    wxConcatFiles(filePCK, filePKX, filePCKX);
    wxPrintf(wxT("Removing: .pck + .pkx\n"));
    wxRemoveFile(filePCK);
    wxRemoveFile(filePKX);
    wxPrintf(wxT("Renaming: .pckx => .pck\n"));
    wxRenameFile(filePCKX, filePCK);
}

/*
 * Split a file into its pck and pkx parts and delte the input file
 *
 * @param[in] fileIn Path to the temporary merged file pck + pkx
 *
 * @return
 */
void splitPCK(wxString fileIn) {
    // FIXME: check if fileIn ends with .pckx and not .pck
    //wxPrintf(wxT("Operation Mode: Split into PCK + PKX Files\n\n");

    wxString filePCK = fileIn;
    wxString filePKX = fileIn.BeforeLast('.') + wxT(".pkx");
    wxString filePCKX = fileIn.BeforeLast('.') + wxT(".pckx");

    size_t fileSize = (size_t)wxFileName::GetSize(filePCK).ToULong();
    // check if fileIn is larger then  2.147.483.392 / 2.147.483.648byte
    if(fileSize < 2147483392+1) {
        wxPrintf(wxT("Nothing to be done\n"));
        return;
    }

    wxPrintf(wxT("Renaming: .pck => .pckx\n"));
    wxRenameFile(filePCK, filePCKX);
    wxPrintf(wxT("Splitting: .pckx => .pck + .pkx\n"));
    wxFFileInputStream fis(filePCKX);
    segmentation(&fis, filePCK, 0, 2147483392);
    segmentation(&fis, filePKX, 2147483392, fileSize);
    wxPrintf(wxT("Removing: .pckx\n"));
    wxRemoveFile(filePCKX);
}

/*
    deflate a patch file
*/
void decompress(wxString fileIn, wxString fileOut)
{
    if(!wxFile::Exists(fileOut))
    {
        wxFFileInputStream fis(fileIn);
        wxUint32 sizeDecompressed;
        fis.Read(&sizeDecompressed, 4);
        wxUint32 sizeCompressed = fis.GetSize()-4;
        wxByte* buffer = new wxByte[sizeCompressed];
        fis.Read(buffer, sizeCompressed);

        wxFFileOutputStream fos(fileOut);
        if(sizeCompressed < sizeDecompressed)
        {
            wxByte* zipBuffer = deflate(buffer, sizeCompressed, sizeDecompressed);
            fos.Write(zipBuffer, sizeDecompressed);
            wxDELETEA(zipBuffer);
        }
        else
        {
            fos.Write(buffer, sizeCompressed);
        }
        fos.Close();

        wxDELETEA(buffer);
    }
}


/*
    returns the base64 encoded entry
*/
// FIXME: no linux support
wxString encodeBase64Entry(wxString decodedPath, wxCSConv encoding)
{
    wxString temp;
    wxString result = wxT("");

    while(decodedPath.Contains(wxT("\\")))
    {
        // attention: reversed order
        temp = decodedPath.AfterLast('\\');

        temp = Base64::Encode(temp, encoding);

        result = wxT("\\") + temp + result;

        decodedPath = decodedPath.BeforeLast('\\');
    }

    return(result);
}

/*
    returns the base64 decoded entry
*/
wxString decodeBase64Entry(wxString encodedPath, wxCSConv encoding)
{
    wxString temp;
    wxString result = wxT("");

    while(encodedPath.Contains(wxFileName::GetPathSeparator()))
    {
        // attention: reversed order
        temp = encodedPath.AfterLast(wxFileName::GetPathSeparator());

        temp = Base64::Decode(temp, encoding);

        result = wxFileName::GetPathSeparator() + temp + result;

        encodedPath = encodedPath.BeforeLast(wxFileName::GetPathSeparator());
    }

    return(result);
}

wxByte* writeTableEntry(fileTableEntry fte, wxUint32& sizeCompressed, bool compress)
{
    wxByte* buffer = new wxByte[ENTRY_SIZE];
    wxMemoryOutputStream mos;
    wxDataOutputStream bos(mos);
    mos.Write(fte.filePath, 260);
    bos.Write32(fte.fileDataOffset);
    bos.Write32(fte.fileDataDecompressedSize);
    bos.Write32(fte.fileDataCompressedSize);
    bos.Write32(0);
    mos.CopyTo(buffer, ENTRY_SIZE);
    if(compress)
    {
        wxByte* pBuffer = buffer;
        buffer = inflate(buffer, ENTRY_SIZE, sizeCompressed, COMPRESSION_LEVEL);
        wxDELETEA(pBuffer);
    }

    return buffer;
}

fileTableEntry readTableEntry(wxByte* buffer, wxUint32 size, bool compressed)
{
    fileTableEntry fte;
    fte.filePath = new wxByte[260];

    if(compressed)
    {
        wxByte* pBuffer = buffer;
        buffer = deflate(buffer, size, ENTRY_SIZE);
        wxDELETEA(pBuffer);
    }

    wxMemoryInputStream mis(buffer, ENTRY_SIZE);
    wxDataInputStream bis(mis);
    mis.Read(fte.filePath, 260);
    fte.fileDataOffset = bis.Read32();
    fte.fileDataDecompressedSize = bis.Read32();
    fte.fileDataCompressedSize = bis.Read32();
    return fte;
}

/*
    creates all directories from the given path, if they don't exist
*/
void createPath(wxString rootDirectory, wxString subPath)
{
    rootDirectory.Append(wxFileName::GetPathSeparator());
    #ifdef __WINDOWS__
    subPath.Replace(wxT("/"), wxString(wxFileName::GetPathSeparator()), true);
    #endif

    while(subPath.Contains(wxFileName::GetPathSeparator()))
    {
        rootDirectory.Append(subPath.BeforeFirst(wxFileName::GetPathSeparator()) + wxFileName::GetPathSeparator());
        subPath = subPath.AfterFirst(wxFileName::GetPathSeparator());
        if(!wxDirExists(rootDirectory))
        {
            wxMkdir(rootDirectory);
        }
    }
}

/*
    Extract the pck file to a directory
    corresponding to the filename
*/
void extract(wxString file)
{
    wxPrintf(wxT("Operation Mode: Extract Files\n\n") + file + wxT("\n\n"));

    mergePCK(file);

    wxCSConv enc(wxFONTENCODING_GB2312);
    wxString rootPath = file + wxT(".files");
    wxString subPath;
    wxFFileInputStream fis(file);
    wxDataInputStream bis(fis);
    fis.SeekI(-8, wxFromEnd);
    wxUint32 entryCount = bis.Read32();
    fis.SeekI(-272, wxFromEnd);
    wxUint32 fileTableOffset = bis.Read32() xor KEY_1;
    fis.SeekI(fileTableOffset, wxFromStart);
    fileTableEntry fileTable[entryCount];
    wxUint32 entrySize;
    wxByte* buffer;
    wxByte* zipBuffer;

    // read file entries
    for(wxUint32 i=0; i<entryCount; i++)
    {
        wxPrintf(wxString::Format(wxT("\rReading File Entries: %i/%i"), (i+1), entryCount));

        entrySize = bis.Read32() xor KEY_1;
        entrySize = bis.Read32() xor KEY_2;

        buffer = new wxByte[entrySize];
        fis.Read(buffer, entrySize);

        // use zlib decompression if compressed_size < decompressed_size
        if(entrySize < ENTRY_SIZE)
        {
            fileTable[i] = readTableEntry(buffer, entrySize, true);
        }
        // no zlib
        else
        {
            fileTable[i] = readTableEntry(buffer, entrySize, false);
        }

        //wxDELETEA(buffer);
    }

    wxPrintf(wxT("\n"));

    if(!wxDirExists(rootPath))
    {
        wxMkdir(rootPath);
    }

    for(wxUint32 i=0; i<entryCount; i++)
    {
        wxPrintf(wxString::Format(wxT("\rExtracting Files: %i/%i"), (i+1), entryCount));

        // table entries contains path in windows format -> convert path seperator to platform
        subPath = wxString((char*)fileTable[i].filePath, enc);
        #ifndef __WINDOWS__
        subPath.Replace(wxT("\\"), wxString(wxFileName::GetPathSeparator()), true);
        #endif
        createPath(rootPath, subPath);

        buffer = new wxByte[fileTable[i].fileDataCompressedSize];

        wxFFileOutputStream fos(rootPath + wxFileName::GetPathSeparator() + subPath);
        fis.SeekI(fileTable[i].fileDataOffset, wxFromStart);
        fis.Read(buffer, fileTable[i].fileDataCompressedSize);

        // use zlib decompression if compressed_size < decompressed_size
        if(fileTable[i].fileDataCompressedSize < fileTable[i].fileDataDecompressedSize)
        {
            zipBuffer = deflate(buffer, fileTable[i].fileDataCompressedSize, fileTable[i].fileDataDecompressedSize);
            fos.Write(zipBuffer, fileTable[i].fileDataDecompressedSize);
            wxDELETEA(zipBuffer);
        }
        // no zlib
        else
        {
            fos.Write(buffer, fileTable[i].fileDataCompressedSize);
        }

        wxDELETEA(buffer);
    }

    wxPrintf(wxT("\n"));
}

/*
    Compress all files from this directory (recursively)
    to the pck file corresponding to the path name
*/
void compress(wxString directory)
{
    wxPrintf(wxT("Operation Mode: Compress Files\n\n") + directory + wxT("\n\n"));

    wxString file = directory.BeforeLast('.');

    wxArrayString files;
    wxDirTraverserFiles fileTraverser(files);
    wxDir(directory).Traverse(fileTraverser);

    wxCSConv enc(wxFONTENCODING_GB2312);
    wxByte* buffer;
    wxByte* zipBuffer;
    wxUint32 entryCount = files.Count();
    wxUint32 fileTableOffset;
    fileTableEntry fileTable[entryCount];
    wxUint32 entrySize;

    wxFFileOutputStream fos(file);
    wxDataOutputStream bos(fos);
    bos.Write32(FSIG_1);
    bos.Write32(0); // placeholder for filesize
    bos.Write32(FSIG_2);

    for(wxUint32 i=0; i<entryCount; i++)
    {
        wxPrintf(wxString::Format(wxT("\rCompressing Files: %i/%i"), (i+1), entryCount));

        wxString winPath = files[i].Mid(directory.Length()+1);
        #ifndef __WINDOWS__
        winPath.Replace(wxString(wxFileName::GetPathSeparator()), wxT("\\"));
        #endif
        fileTable[i].filePath = fillPath((wxByte*)winPath.mb_str(enc).release());

        fileTable[i].fileDataOffset = fos.TellO();
        wxFFileInputStream fis(files[i]);
        fileTable[i].fileDataDecompressedSize = fis.GetSize();
        buffer = new wxByte[fileTable[i].fileDataDecompressedSize];
        fis.Read(buffer, fileTable[i].fileDataDecompressedSize);

        zipBuffer = inflate(buffer, fileTable[i].fileDataDecompressedSize, fileTable[i].fileDataCompressedSize, COMPRESSION_LEVEL);

        // use zlib compression if compressed_size < decompressed_size
        if(fileTable[i].fileDataCompressedSize < fileTable[i].fileDataDecompressedSize)
        {
            fos.Write(zipBuffer, fileTable[i].fileDataCompressedSize);
        }
        // no zlib
        else
        {
            fos.Write(buffer, fileTable[i].fileDataDecompressedSize);
            fileTable[i].fileDataCompressedSize = fileTable[i].fileDataDecompressedSize;
        }

        wxDELETEA(zipBuffer);
        wxDELETEA(buffer);
    }

    fileTableOffset = fos.TellO();

    wxPrintf(wxT("\n"));

    // write file entries
    for(wxUint32 i=0; i<entryCount; i++)
    {
        wxPrintf(wxString::Format(wxT("\rWriting File Entries: %i/%i"), (i+1), entryCount));

        zipBuffer = writeTableEntry(fileTable[i], entrySize, true);

        if(entrySize > ENTRY_SIZE)
        {
            entrySize = ENTRY_SIZE;
        }

        bos.Write32(entrySize xor KEY_1);
        bos.Write32(entrySize xor KEY_2);

        // use zlib compression if compressed_size < decompressed_size
        if(entrySize < ENTRY_SIZE)
        {
            fos.Write(zipBuffer, entrySize);
        }
        // no zlib
        else
        {
            buffer = writeTableEntry(fileTable[i], entrySize, false);
            fos.Write(buffer, entrySize);
            wxDELETEA(buffer);
        }

        wxDELETEA(zipBuffer);
    }

    bos.Write32(ASIG_1);
    bos.Write16(2);
    bos.Write16(2);
    bos.Write32(fileTableOffset xor KEY_1);
    bos.Write32(0); // write int=0 for newer versions (seperator)
    fos.Write("Angelica File Package, Perfect World.", 37);
    wxByte* zeros = new wxByte[215]; //write only 215 zeros instead of 219 for newer versions
    for(wxUint32 i=0; i<215; i++)
    {
        zeros[i] = 0;
    }
    fos.Write(zeros, 215);
    wxDELETEA(zeros);
    bos.Write32(ASIG_2);
    bos.Write32(entryCount);
    bos.Write16(2);
    bos.Write16(2);

    wxUint32 fileSize = fos.TellO();
    fos.SeekO(4, wxFromStart);
    bos.Write32(fileSize);

    wxPrintf(wxT("\n"));

    splitPCK(file);
}

/*
    Add all files from this directory (recursively)
    to the pck file corresponding to the path name
*/
void add(wxString directory, bool isBase64)
{
    wxPrintf(wxT("Operation Mode: Add Files\n\n") + directory + wxT("\n\n"));

    wxString pckFile = directory.BeforeLast('.');
    mergePCK(pckFile);

    wxArrayString files;
    wxDirTraverserFiles fileTraverser(files);
    wxDir(directory).Traverse(fileTraverser);
    wxUint32 entryCountAdd = files.Count();
    wxCSConv enc(wxFONTENCODING_GB2312);
    pckFile.Replace(wxT(".b64"), wxT(""));
    wxFFileOutputStream fout(pckFile, wxT("r+b"));
    wxDataOutputStream bout(fout);
    wxFFileInputStream fin(pckFile, wxT("r+b"));
    wxDataInputStream bin(fin);
    fin.SeekI(-8, wxFromEnd);
    wxUint32 entryCountOld = bin.Read32();
    fin.SeekI(-272, wxFromEnd);
    wxUint32 fileTableOffset = bin.Read32() xor KEY_1;
    wxUint32 entryCount = entryCountOld+entryCountAdd;
    fileTableEntry fileTable[entryCount];
    wxUint32 entrySize;
    wxByte* buffer;
    wxByte* zipBuffer;

    fin.SeekI(fileTableOffset, wxFromStart);
    // read file entries from pck
    for(wxUint32 i=0; i<entryCountOld; i++)
    {
        wxPrintf(wxString::Format(wxT("\rReading File Entries: %i/%i"), (i+1), entryCountOld));

        entrySize = bin.Read32() xor KEY_1;
        entrySize = bin.Read32() xor KEY_2;

        buffer = new wxByte[entrySize];
        fin.Read(buffer, entrySize);

        // use zlib decompression if compressed_size < decompressed_size
        if(entrySize < ENTRY_SIZE)
        {
            fileTable[i] = readTableEntry(buffer, entrySize, true);
        }
        // no zlib
        else
        {
            fileTable[i] = readTableEntry(buffer, entrySize, false);
        }

        //wxDELETEA(buffer);
    }

    wxPrintf(wxT("\n"));

    fout.SeekO(fileTableOffset, wxFromStart);
    // add new files and file entries from directory
    for(wxUint32 i=entryCountOld; i<entryCount; i++)
    {
        wxPrintf(wxString::Format(wxT("\rAdding Files: %i/%i"), (i-entryCountOld+1), entryCountAdd));

        wxString winPath = files[i-entryCountOld].Mid(directory.Length()+1);
        if(isBase64)
        {
            winPath = decodeBase64Entry(wxFileName::GetPathSeparator() + winPath, enc);
        }
        #ifndef __WINDOWS__
        winPath.Replace(wxString(wxFileName::GetPathSeparator()), wxT("\\"));
        #endif
        fileTable[i].filePath = fillPath((wxByte*)winPath.mb_str(enc).release());

        fileTable[i].fileDataOffset = fout.TellO();
        wxFFileInputStream fis(files[i-entryCountOld]);
        fileTable[i].fileDataDecompressedSize = fis.GetSize();
        buffer = new wxByte[fileTable[i].fileDataDecompressedSize];
        fis.Read(buffer, fileTable[i].fileDataDecompressedSize);

        zipBuffer = inflate(buffer, fileTable[i].fileDataDecompressedSize, fileTable[i].fileDataCompressedSize, COMPRESSION_LEVEL);

        // use zlib compression if compressed_size < decompressed_size
        if(fileTable[i].fileDataCompressedSize < fileTable[i].fileDataDecompressedSize)
        {
            fout.Write(zipBuffer, fileTable[i].fileDataCompressedSize);
        }
        // no zlib
        else
        {
            fout.Write(buffer, fileTable[i].fileDataDecompressedSize);
            fileTable[i].fileDataCompressedSize = fileTable[i].fileDataDecompressedSize;
        }

        wxDELETEA(zipBuffer);
        wxDELETEA(buffer);
    }

    wxPrintf(wxT("\n"));
    wxUint32 replacedCount = 0;
    fileTableOffset = fout.TellO();

    // write file entries
    for(wxUint32 i=0; i<entryCount; i++)
    {
        // check if the current file entry was replaced by a newer one
        for(wxUint32 n=entryCountOld; n<entryCount; n++)
        {
            if(i<entryCountOld && compare(fileTable[n].filePath, fileTable[i].filePath, 260))
            {
                // this entry was replaced and will not be written
                replacedCount++;
                break;
            }
            if(i>=entryCountOld || n==entryCount-1)
            {
                zipBuffer = writeTableEntry(fileTable[i], entrySize, true);

                if(entrySize > ENTRY_SIZE)
                {
                    entrySize = ENTRY_SIZE;
                }

                bout.Write32(entrySize xor KEY_1);
                bout.Write32(entrySize xor KEY_2);

                // use zlib compression if compressed_size < decompressed_size
                if(entrySize < ENTRY_SIZE)
                {
                    fout.Write(zipBuffer, entrySize);
                }
                // no zlib
                else
                {
                    buffer = writeTableEntry(fileTable[i], entrySize, false);
                    fout.Write(buffer, entrySize);
                    wxDELETEA(buffer);
                }

                wxDELETEA(zipBuffer);
                break;
            }
        }

        wxPrintf(wxString::Format(wxT("\rRe-Writing File Entries: %i/%i (%i Replacements)"), (i+1-replacedCount), entryCount, replacedCount));
    }

    bout.Write32(ASIG_1);
    bout.Write16(2);
    bout.Write16(2);
    bout.Write32(fileTableOffset xor KEY_1);
    bout.Write32(0); // write int=0 for newer versions (seperator)
    fout.Write("Angelica File Package, Perfect World.", 37);
    wxByte* zeros = new wxByte[215]; //write only 215 zeros instead of 219 for newer versions
    for(wxUint32 i=0; i<215; i++)
    {
        zeros[i] = 0;
    }
    fout.Write(zeros, 215);
    wxDELETEA(zeros);
    bout.Write32(ASIG_2);
    bout.Write32(entryCount-replacedCount);
    bout.Write16(2);
    bout.Write16(2);

    wxUint32 fileSize = fout.TellO();
    fout.SeekO(4, wxFromStart);
    bout.Write32(fileSize);

    wxPrintf(wxT("\n"));

    splitPCK(pckFile);
}

/*
    Extract a cup file to a directory
    corresponding to the filename

    After extraction the filenames are decoded
    and the file contents are deflated
*/
void decode(wxString directory)
{
    wxPrintf(wxT("Operation Mode: Extract Patch\n\n") + directory + wxT("\n"));

    wxCSConv enc(wxT("UTF-8"));
    wxString directoryOut = directory.BeforeLast('.') + wxT(".decoded");
    if(!wxDir::Exists(directoryOut))
    {
        wxMkdir(directoryOut);
    }

    // reading the file list from all v-*.inc files
    wxArrayString v_incs;
    wxDir::GetAllFiles(directory, &v_incs, wxT("*.inc"), wxDIR_DEFAULT);

    wxString line;
    wxString chDir = wxFileName::GetPathSeparator();
    wxString fileBase64;
    wxString fileDecoded;

    wxTextFile f;

    // we want to extract all content, so we just have to find the v-*.inc with largest revision number
    for(wxUint32 n=0; n<v_incs.Count(); n++)
    {
        wxPrintf(wxT("\nProcessing Index File: ") + v_incs.Item(n).AfterLast('\\') + wxT("\n"));

        f.Open(v_incs.Item(n));

        wxUint32 i=0;
        while(!f.Eof())
        {
            line = f.GetNextLine();
            if(line.StartsWith(wxT("!")) || line.StartsWith(wxT("+")))
            {
                //filesMD5.Add(line.Mid(1).BeforeFirst(' '));
                line = line.AfterFirst(' ');
                #ifdef __WINDOWS__
                line.Replace(wxT("/"), wxString(wxFileName::GetPathSeparator()), true);
                #endif

                // currently file path' are using a "change dir" based system
                // we need to add the root path to all files that are listed after a change dir command
                if(line.StartsWith(wxString(wxFileName::GetPathSeparator())))
                {
                    chDir = line.BeforeLast(wxFileName::GetPathSeparator()) + wxFileName::GetPathSeparator();
                    fileBase64 = line;
                }
                else
                {
                    fileBase64 = chDir + line;
                }

                /*
                    all previous extracted filenames are usually lowercase (lowercase stored in table entries)
                    filenames in v-*.inc contains the genuine base64 filename, containing upper and lower characters
                    windows does not distinguish between upper/lower filenames, but linux does
                    -> we need to lower the filename where required
                */
                // check if this file exists
                if(wxFile::Exists(directory + wxFileName::GetPathSeparator() + wxT("element") + fileBase64.Lower()))
                {
                    fileDecoded = decodeBase64Entry(fileBase64, enc);

                    // create the directory structure for the output file
                    createPath(directoryOut, wxT("element") + fileDecoded);

                    // deflate the encoded file to the new path
                    decompress(directory + wxFileName::GetPathSeparator() + wxT("element") + fileBase64.Lower(), directoryOut + wxFileName::GetPathSeparator() + wxT("element") + fileDecoded);
                }

                wxPrintf(wxString::Format(wxT("\rDecompressing Files: %i"), (i+1)));

                i++;
            }
        }

        f.Close();
    }

    wxPrintf(wxT("\n"));
}

/*
    Create a xup file from a directory
    corresponding to the filename

    After compression the filenames are encoded
    and the file contents are enflated
*/
// FIXME: no linux support
void encode(wxString directory)
{
    wxPrintf(wxT("Operation Mode: Create Patch\n\n") + directory + wxT("\n\n"));

    wxCSConv enc(wxFONTENCODING_GB2312);
    wxArrayString files;
    wxDirTraverserFiles fileTraverser(files);
    wxDir(directory).Traverse(fileTraverser, wxT("*.*"), wxDIR_DEFAULT);

    // create a temp directory for patch
    wxString targetDir = directory + wxT(".TMP");
    if(!wxDir::Exists(targetDir))
    {
        wxMkdir(targetDir);
    }

    wxString decodedFile;
    for(wxUint32 i=0; i<files.Count(); i++)
    {
        wxPrintf(wxString::Format(wxT("\rCreating Temp Files: %i/%i"), (i+1), files.Count()));

        decodedFile = files[i];
        decodedFile.Replace(directory + wxT("\\"), wxT(""));

        if(decodedFile.Contains(wxT(".pck.files")))
        {
            decodedFile.Replace(wxT("element\\"), wxT(""));
            decodedFile.Replace(wxT(".pck.files"), wxT(".pck.b64.files"));
            decodedFile = wxT("element\\") + decodedFile.BeforeFirst('\\') + encodeBase64Entry(wxT("\\") + decodedFile.AfterFirst('\\'), enc);
        }

        // create target directory structure
        createPath(targetDir, decodedFile);

        // copy source file to target file...
        wxCopyFile(files[i], targetDir + wxT("\\") + decodedFile);
    }

    // compress
    wxPrintf(wxT("\nCompressing Files..."));
    wxProcess::Open(wxT("sza.exe a -t7z -mx9 -r \"") + targetDir.BeforeLast('\\') + wxT("\\ec_patch_0-0.xup\" \"") + targetDir + wxT("\\*\""), wxEXEC_SYNC);

    // delete temp directory recursive
    wxPrintf(wxT("\nDeleting Temp Files..."));
    wxDeldir(targetDir);
}

IMPLEMENT_APP(pckApp);

bool pckApp::OnInit()
{
    // check if amount of command line arguments is correct
    // first parameter is the execuable file itself
    // second is the game mode
    // third is the instruction
    // fourth is the file/directory
    // fifth is optional compression level

    if(argc < 4)
    {
        print_help();
        exit(1);
    }

    // Convert first parameter argv[1] from char* to wxString
    wxString gamemode(argv[1], wxConvUTF8);
    // Convert second parameter argv[2] from char* to wxString
    wxString instruction(argv[2], wxConvUTF8);
    // Convert third parameter argv[3] from char* to wxString
    wxString path(argv[3], wxConvUTF8);
    // Convert fourth parameter argv[4] from char* to int
    if(argc > 4)
    {
        COMPRESSION_LEVEL = wxAtoi(argv[4]);
        if(COMPRESSION_LEVEL < 0)
        {
            COMPRESSION_LEVEL = 0;
        }
        if(COMPRESSION_LEVEL > 9)
        {
            COMPRESSION_LEVEL = 9;
        }
    }

    // file signature for all games
    {
        FSIG_1 = 1305093103;
        FSIG_2 = 1453361591;
    }
    // perfect world & jade dynasty
    if(gamemode == wxT("-pw") || gamemode == wxT("-jw"))
    {
        KEY_1 = -1466731422;
        KEY_2 = -240896429;
        ASIG_1 = -33685778;
        ASIG_2 = -267534609;
    }
    // forsaken world
    if(gamemode == wxT("-fw"))
    {
        KEY_1 = 566434367;
        KEY_2 = 408690725;
        ASIG_1 = -1526153788;
        ASIG_2 = -2060097592;
    }
    // ether sage
    if(gamemode == wxT("-eso"))
    {
        KEY_1 = -1228069623;
        KEY_2 = 1822409141;
        ASIG_1 = 1571301968;
        ASIG_2 = 2043846474;
    }
    // rwp dance (steps)
    if(gamemode == wxT("-rwpd"))
    {
        KEY_1 = 711164174;
        KEY_2 = 839959661;
        ASIG_1 = -1424846705;
        ASIG_2 = -1289545470;
    }

    if(instruction != wxT("-x") && instruction != wxT("-c") && instruction != wxT("-a") && instruction != wxT("-ap") && instruction != wxT("-xp") && instruction != wxT("-cp"))
    {
        wxPrintf(wxT("Second argument is not a valid instruction\n"));
        exit(2);
    }

    if(instruction == wxT("-x"))
    {
        // Check if path is a valid file
        if(!wxFileExists(path))
        {
            wxPrintf(wxT("Third argument is not a valid file\n"));
            exit(3);
        }
        else
        {
            extract(path);
        }
    }

    if(instruction == wxT("-c"))
    {
        // Check if path is a valid directory
        if(!wxDirExists(path) || !path.EndsWith(wxT(".pck.files")))
        {
            wxPrintf(wxT("Third argument is not a valid directory\n"));
            exit(4);
        }
        else
        {
            compress(path);
        }
    }

    if(instruction == wxT("-a"))
    {
        // Check if path is a valid directory
        if(!wxDirExists(path))
        {
            wxPrintf(wxT("Third argument is not a valid directory\n"));
            exit(5);
        }
        else
        {
            add(path, false);
        }
    }

    if(instruction == wxT("-ap"))
    {
        // Check if path is a valid directory
        if(!wxDirExists(path))
        {
            wxPrintf(wxT("Third argument is not a valid directory\n"));
            exit(5);
        }
        else
        {
            add(path, true);
        }
    }

    if(instruction == wxT("-xp"))
    {
        // Check if path is a valid file
        if(!wxFileExists(path))
        {
            wxPrintf(wxT("Third argument is not a valid file\n"));
            exit(6);
        }
        else
        {
            extract(path);
            wxPrintf(wxT("\n\n\n"));
            decode(path + wxT(".files"));
        }
    }

    if(instruction == wxT("-cp"))
    {
        // Check if path is a valid directory
        if(!wxDirExists(path))
        {
            wxPrintf(wxT("Third argument is not a valid directory\n"));
            exit(7);
        }
        else
        {
            encode(path);
        }
    }

    exit(0);
    return false;
}
