#include <Windows.h>
#include <process.h>
#include <iostream>
using namespace std;
HANDLE trac,allo;
unsigned long dwPageSize;
LPVOID lpvBase;
BOOL end_sig;
// two handles

void FormatMemInfo(MEMORY_BASIC_INFORMATION &meminfo)
{
    // this function gives you a human-readable formatted output of struct meminfo

    // use local variables for short
    PVOID base_address  = meminfo.BaseAddress;  // ***
    PVOID alloc_base    = meminfo.AllocationBase;
    DWORD alloc_protect = meminfo.AllocationProtect;
    DWORD region_size   = meminfo.RegionSize;  // ***
    DWORD state         = meminfo.State;  // ***
    DWORD protect       = meminfo.Protect;  // ***
    DWORD type          = meminfo.Type;

    // format the AllocationProtect field
    std::string s_alloc_protect;
    if(alloc_protect & PAGE_NOACCESS)                // 0x0001
        s_alloc_protect = "NoAccess";
    if(alloc_protect & PAGE_READONLY)                // 0x0002
        s_alloc_protect = "Readonly";
    else if(alloc_protect & PAGE_READWRITE)          // 0x0004
        s_alloc_protect = "ReadWrite";
    else if(alloc_protect & PAGE_WRITECOPY)          // 0x0008
        s_alloc_protect = "WriteCopy";
    else if(alloc_protect & PAGE_EXECUTE)            // 0x0010
        s_alloc_protect = "Execute";
    else if(alloc_protect & PAGE_EXECUTE_READ)       // 0x0020
        s_alloc_protect = "Execute_Read";
    else if(alloc_protect & PAGE_EXECUTE_READWRITE)  // 0x0040
        s_alloc_protect = "Execute_ReadWrite";
    else if(alloc_protect & PAGE_EXECUTE_WRITECOPY)  // 0x0080
        s_alloc_protect = "Execute_WriteCopy";
    if(alloc_protect & PAGE_GUARD)                   // 0x0100
        s_alloc_protect += "+Guard";
    if(alloc_protect & PAGE_NOCACHE)                 // 0x0200
        s_alloc_protect += "+NoCache";

    // format the State field
    std::string s_state;
    if(state == MEM_COMMIT) // accessible, physical memory is allocated.
        s_state = "Commit ";
    else if(state == MEM_FREE) // unaccessible, AllocationBase, AllocationProtect, Protect, and Type are undefined.
        s_state = "Free   ";
    else if(state == MEM_RESERVE) // unaccessible, Protect is undefined.
        s_state = "Reserve";
    else  // this case is not expected to happen
        s_state = "Damned ";

    // format the Protect field
    std::string s_protect;
    if(protect & PAGE_NOACCESS)
        s_protect = "NoAccess";
    if(protect & PAGE_READONLY)
        s_protect = "Readonly";
    else if(protect & PAGE_READWRITE)
        s_protect = "ReadWrite";
    else if(protect & PAGE_WRITECOPY)
        s_protect = "WriteCopy";
    else if(protect & PAGE_EXECUTE)
        s_protect = "Execute";
    else if(protect & PAGE_EXECUTE_READ)
        s_protect = "Execute_Read";
    else if(protect & PAGE_EXECUTE_READWRITE)
        s_protect = "Execute_ReadWrite";
    else if(protect & PAGE_EXECUTE_WRITECOPY)
        s_protect = "Execute_WriteCopy";
    if(protect & PAGE_GUARD) 
        s_protect += "+Guard";
    if(protect & PAGE_NOCACHE)
        s_protect += "+NoCache";

    // format the Type field
    std::string s_type;
    if(type == MEM_IMAGE)
        s_type = "Image  ";
    else if(type == MEM_MAPPED)
        s_type = "Free   ";
    else if(type == MEM_PRIVATE)  // most cases
        s_type = "Private";
    else
        s_type = "-      ";

	cout<<"BaseAddress:"<<'\t'<<base_address<<'\n';
	cout<<"AllocationBase:"<<'\t'<<alloc_base<<'\n';
	cout<<"AllocationProtect:"<<'\t'<<s_alloc_protect.c_str()<<'\n';
	cout<<"RegionSize:"<<'\t'<<region_size<<'\n';
	cout<<"State:"<<'\t'<<s_state.c_str()<<'\n';
	cout<<"Protect:"<<'\t'<<s_protect.c_str()<<'\n';
	cout<<"Type:"<<'\t'<<s_type.c_str()<<'\n';
	cout<<'\n';
}

unsigned __stdcall Tracker(void *)
{	// Track the virtual memory manipulations of Allocator
	
	// Wait for Allocator
	while(!end_sig)
	{
		WaitForSingleObject(allo,INFINITE);
		//
		// Do something here
		MEMORY_BASIC_INFORMATION lpBuffer;
		if(VirtualQuery(lpvBase,&lpBuffer,sizeof(lpBuffer)) == 0)
			cout<<"VirtualQuery Error!";
		FormatMemInfo(lpBuffer);  // format
		//
		ReleaseSemaphore(trac,1,NULL);
	}
	return 1;
}

unsigned __stdcall Allocator(void*)
{

	// Wait for Tracker
	WaitForSingleObject(trac,INFINITE);

	// allocate a page
	lpvBase = VirtualAlloc(NULL,dwPageSize,MEM_RESERVE,PAGE_READWRITE);
	if(lpvBase == NULL)
	{
		cout<<"VirtualAlloc Reserve Error!";
		exit(1);
	}
	ReleaseSemaphore(allo,1,NULL);
	WaitForSingleObject(trac,INFINITE);

	//commit a page
	lpvBase = VirtualAlloc(lpvBase,dwPageSize,MEM_COMMIT,PAGE_READWRITE);
	if(lpvBase == NULL)
	{
		cout<<"VirtualAlloc Commit Error!";
		exit(1);
	}
	ReleaseSemaphore(allo,1,NULL);
	WaitForSingleObject(trac,INFINITE);

	//lock a page
	if(VirtualLock(lpvBase,dwPageSize) == NULL)
	{
		cout<<"VirtualLock Error!";
		exit(1);
	}
	ReleaseSemaphore(allo,1,NULL);
	WaitForSingleObject(trac,INFINITE);

	// unlock a page
	if(VirtualUnlock(lpvBase,dwPageSize) == NULL)
	{
		cout<<"VirtualUnlock Error!";
		exit(1);
	}
	ReleaseSemaphore(allo,1,NULL);
	WaitForSingleObject(trac,INFINITE);
	
	if(VirtualFree(lpvBase,0,MEM_RELEASE) == 0)
	{
		cout<<"VirtualFree Error!";
		exit(1);
	}
	end_sig = 1;
	ReleaseSemaphore(allo,1,NULL);
	return 2;
}

int main()
{
	// this signal records the termination of Allocator
	// if it's true, Tracker would terminate also.
	end_sig = FALSE;
	SYSTEM_INFO siSysInfo;
	GetSystemInfo(&siSysInfo); 
	dwPageSize = siSysInfo.dwPageSize;
	
	// Create Semaphores
	trac = CreateSemaphore(NULL,1,1,NULL);
	allo = CreateSemaphore(NULL,0,1,NULL);
	HANDLE h1, h2;

	//Create Threads
	h1 = (HANDLE)_beginthreadex(NULL,0,Tracker,NULL,0,NULL);
	h2 = (HANDLE)_beginthreadex(NULL,0,Allocator,NULL,0,NULL);

	//Wait for threads to terminate
	WaitForSingleObject(h1,INFINITE);
	WaitForSingleObject(h2,INFINITE);

	//Close those handles
	CloseHandle(h1);
	CloseHandle(h2);
	CloseHandle(trac);
	CloseHandle(allo);
}