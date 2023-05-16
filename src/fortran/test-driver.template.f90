subroutine getoutdir(outdir, lenoutdir)
  character*256, intent(out) :: outdir
  integer, intent(out) :: lenoutdir

  outdir = "{OUTPUT_DIR}"

  lenoutdir = len_trim(outdir)

end subroutine getoutdir

subroutine vgetoutdir(outdir, lenoutdir)
  character*256, intent(out) :: outdir
  integer, intent(out) :: lenoutdir
  
  call getoutdir(outdir, lenoutdir)

end subroutine vgetoutdir

program forttest_driver
  {USE_MODULES}
  use naturalFRUIT
  implicit none

  interface
    subroutine test_sub()
    end subroutine test_sub
  end interface
  
  type test_t
    character(:), allocatable :: name
    procedure(test_sub), pointer, nopass :: test_sub
  end type test_t

  type testsuite_t
    character(:), allocatable :: name
    type(test_t), allocatable :: tests(:)
  end type testsuite_t

  type(test_t), allocatable :: test_routines(:)
  type(testsuite_t), allocatable :: testsuites(:)

  integer :: i, j, nfailed, n

  nfailed = 0
  testsuites = {TEST_ARRAY}

  do i=1,size(testsuites)

    call testsuite_initialize()

    do j=1,size(testsuites(i)%tests)

      call testcase_initialize(testsuites(i)%tests(j)%name)
      call testsuites(i)%tests(j)%test_sub()
      call testcase_finalize()

    end do
    
    call testsuite_summary()
    call testsuite_finalize(n)

    nfailed = nfailed + n

  end do

  call exit(nfailed)

end program forttest_driver
