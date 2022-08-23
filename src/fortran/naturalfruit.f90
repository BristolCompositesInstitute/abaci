!----------------------------------------------------------
! naturalFRUIT
! VERSION: 0.2
! LICENSE: BSD-3-Clause
!
! Original author: Andrew H. Chen meihome@gmail.com
! Modified by: Cibin Joseph cibinjoseph92@gmail.com
!----------------------------------------------------------
!
! This work is derived from FRUIT,
! Unit test framework for FORTRAN.  (FoRtran UnIT)
!
! This module is to perform unit testing for FORTRAN subroutines
! The methods used most are: assert_true, assert_equal
!

module naturalfruit
  !! Summary: This module contains fruit procedures and variables
  !! This module contains the procedures and variables that the user may use
  !! for unit testing with fruit.
  implicit none
  private

  integer, parameter :: dp = kind(1.0d0)  !! Double precision
  real, parameter :: eps = epsilon(1.0)  !! Machine epsilon
  real, parameter :: eps_dp = epsilon(1.0d0)  !! Machine epsilon

  integer, parameter :: STDOUT_DEFAULT = 6
  integer :: stdout = STDOUT_DEFAULT

  integer, parameter :: XML_OPEN = 20
  integer, parameter :: XML_WORK_DEFAULT = 21
  integer :: xml_work = XML_WORK_DEFAULT
  character(len=*), parameter :: xml_filename = "result.xml"
  character(len=*), parameter :: XML_FN_WORK_DEF = "result_tmp.xml"
  character(len=50) :: xml_filename_work = XML_FN_WORK_DEF

  integer, parameter :: MAX_NUM_FAILURES_IN_XML = 10
  integer, parameter :: XML_LINE_LENGTH = 2670
  ! xml_line_length >= max_num_failures_in_xml * (msg_length + 1) + 50

  integer, parameter :: STRLEN_T = 12

  integer, parameter :: NUMBER_LENGTH = 10

  integer, parameter :: MSG_LENGTH = 256
  integer, parameter :: MAX_MSG_STACK_SIZE = 2000
  integer, parameter :: MSG_ARRAY_INCREMENT = 50
  integer, parameter :: MAX_MARKS_PER_LINE = 78

  character(*), parameter :: DEFAULT_CASE_NAME = '_not_set_'
  logical, private, parameter :: DEFAULT_CASE_PASSED = .true.

  !---------- save ----------
  integer, private, save :: successful_assert_count = 0
  integer, private, save :: failed_assert_count = 0
  integer, private, save :: initial_failed_assert_count = 0

  integer, private, save :: message_index = 1
  integer, private, save :: message_index_from = 1
  integer, private, save :: current_max = 50

  character(len=MSG_LENGTH), private, allocatable :: message_array(:)
  character(len=MSG_LENGTH), private, save :: msg = '[case name not set from set_name]: '
  character(len=MSG_LENGTH), private, save :: case_name = DEFAULT_CASE_NAME

  integer, private, save :: successful_case_count = 0
  integer, private, save :: failed_case_count = 0
  integer, private, save :: testCaseIndex = 1
  logical, private, save :: last_passed = .false.
  logical, private, save :: case_passed = DEFAULT_CASE_PASSED
  integer, private, save :: case_time_from = 0
  integer, private, save :: linechar_count = 0
  logical, private, save :: if_show_dots = .true.

  integer, parameter :: FRUIT_PREFIX_LEN_MAX = 50
  character(len=FRUIT_PREFIX_LEN_MAX) :: prefix = ""
  !---------- save ----------

  type ty_stack
    !! display: none
    integer :: successful_assert_count, failed_assert_count
    integer :: initial_failed_assert_count

    integer :: message_index
    integer :: message_index_from
    integer :: current_max

    character(len=MSG_LENGTH), pointer :: message_array(:)
    character(len=MSG_LENGTH) :: case_name !  = DEFAULT_CASE_NAME

    integer :: successful_case_count, failed_case_count
    integer :: testCaseIndex
    logical :: last_passed
    logical :: case_passed = DEFAULT_CASE_PASSED
    integer :: case_time_from
    integer :: linechar_count
    logical :: if_show_dots
  end type ty_stack

  type(ty_stack), save :: stashed_suite

  public :: FRUIT_PREFIX_LEN_MAX
  private :: to_s

  ! Assert subroutines
  public :: assert_equal, assert_not_equal
  public :: assert_true, assert_false
  public :: assert_identical, assert_not_identical

  ! Common testing subroutines
  public :: testsuite_initialize,  testsuite_finalize
  public :: testcase_initialize, testcase_finalize
  public :: testsuite_summary, testsuite_summary_table
  public :: fruit_if_case_failed, failed_assert_action
  public :: get_total_count, get_failed_count
  public :: get_assert_and_case_count
  public :: get_case_name, set_case_name
  public :: add_success, add_fail
  public :: stash_test_suite, restore_test_suite


  ! Subroutines for checks
  public :: is_last_passed, is_case_passed
  public :: is_all_successful

  ! Message subroutines
  public :: get_last_message
  public :: get_messages, get_message_array
  public :: get_message_index

  ! XML specific subroutines
  public :: testsuite_initialize_xml
  public :: testsuite_summary_xml
  public :: case_passed_xml, case_failed_xml
  public :: get_xml_filename_work, set_xml_filename_work

  ! Override subroutines
  public :: override_stdout, end_override_stdout
  public :: override_xml_work, end_override_xml_work
  public :: fruit_hide_dots, fruit_show_dots
  public :: get_prefix, set_prefix

  private :: findfalse
  ! findloc() intrinsic introduced in Fortran 2008
  ! may be used in place of findfalse.
  ! However, untill gfortran-9 is well adopted by users,
  ! findfalse can be used for ease of setup

  interface assert_equal
    !! category: testcase subroutines
    !! summary: Test that *var1* and *var2* are equal.
    !! Test that *var1* and *var2* are equal.
    !! If the values do not compare equal, the test will fail.<br/><br/>
    !! assert_equal invokes one of the following subroutines according
    !! to the number or type of arguments.
    !====== begin of generated interface ======
    module procedure assert_eq_logical_
    module procedure assert_eq_1d_logical_
    module procedure assert_eq_2d_logical_
    module procedure assert_eq_string_
    module procedure assert_eq_1d_string_
    module procedure assert_eq_2d_string_
    module procedure assert_eq_int_
    module procedure assert_eq_1d_int_
    module procedure assert_eq_2d_int_
    module procedure assert_eq_real_
    module procedure assert_eq_1d_real_
    module procedure assert_eq_2d_real_
    module procedure assert_eq_double_
    module procedure assert_eq_1d_double_
    module procedure assert_eq_2d_double_
    module procedure assert_eq_complex_real_
    module procedure assert_eq_1d_complex_real_
    module procedure assert_eq_2d_complex_real_
    module procedure assert_eq_complex_double_
    module procedure assert_eq_1d_complex_double_
    module procedure assert_eq_2d_complex_double_
    !====== end of generated inteface ======
  end interface

  interface assert_not_equal
    !! category: testcase subroutines
    !! summary: Test that *var1* and *var2* are not equal.
    !! Test that *var1* and *var2* are not equal.
    !! If the values do compare equal, the test will fail.<br/><br/>
    !! assert_not_equal invokes one of the following subroutines according
    !! to the number or type of arguments.
    !====== begin of generated interface ======
    module procedure assert_not_eq_logical_
    module procedure assert_not_eq_1d_logical_
    module procedure assert_not_eq_2d_logical_
    module procedure assert_not_eq_string_
    module procedure assert_not_eq_1d_string_
    module procedure assert_not_eq_2d_string_
    module procedure assert_not_eq_int_
    module procedure assert_not_eq_1d_int_
    module procedure assert_not_eq_2d_int_
    module procedure assert_not_eq_real_
    module procedure assert_not_eq_1d_real_
    module procedure assert_not_eq_2d_real_
    module procedure assert_not_eq_double_
    module procedure assert_not_eq_1d_double_
    module procedure assert_not_eq_2d_double_
    module procedure assert_not_eq_complex_real_
    module procedure assert_not_eq_1d_complex_real_
    module procedure assert_not_eq_2d_complex_real_
    module procedure assert_not_eq_complex_double_
    module procedure assert_not_eq_1d_complex_double_
    module procedure assert_not_eq_2d_complex_double_
    !====== end of generated inteface ======
  end interface

  interface add_fail
    !! category: testsuite subroutine
    !! summary: Print message to screen on assert failure and add to count.
    !! Print message to screen on assert failure and add to count.<br/><br/>
    !! add_fail invokes one of the following subroutines according
    !! to number of arguments.
    module procedure add_fail_
    module procedure add_fail_case_named_
  end interface

  interface to_s
    !! Convert to string
    module procedure to_s_int_
    module procedure to_s_real_
    module procedure to_s_logical_
    module procedure to_s_double_
    module procedure to_s_complex_
    module procedure to_s_double_complex_
    module procedure to_s_string_
  end interface

  interface findfalse
    !! Returns location of first occurence of false value
    module procedure findfalse_1d_
    module procedure findfalse_2d_
  end interface findfalse

contains

  subroutine testsuite_initialize(rank)
    !! category: testsuite subroutine
    !! Initialize FRUIT driver environment.
    integer, intent(in), optional :: rank
    logical :: if_write

    successful_assert_count = 0
    failed_assert_count = 0
    message_index = 1
    message_index_from = 1

    if_write = .true.
    if (present(rank)) then
      if (rank /= 0) if_write = .false.
    endif

    if (if_write) then
      write (stdout, *)
      write (stdout, *) "Test module initialized"
      write (stdout, *)
      write (stdout, *) "   . : successful assert,   F : failed assert "
      write (stdout, *)
    endif
    !$omp critical     (FRUIT_OMP_ALLOCATE_MESSAGE_ARRAY)
    if (.not. allocated(message_array)) then
      allocate (message_array(MSG_ARRAY_INCREMENT))
    end if
    !$omp end critical (FRUIT_OMP_ALLOCATE_MESSAGE_ARRAY)
  end subroutine testsuite_initialize

  subroutine testsuite_finalize(exit_code)
    !! category: testsuite subroutine
    !! summary: Finalize FRUIT driver environment
    !! Finalize FRUIT driver environment and optionally
    !!  return no. of failed cases as an *exit_code*.
    !!  for exception handling
    integer, intent(out), optional :: exit_code
    !$omp critical     (FRUIT_OMP_DEALLOCATE_MESSAGE_ARRAY)
    if (allocated(message_array)) then
      deallocate (message_array)
    endif
    if (present(exit_code)) exit_code = failed_case_count
    !$omp end critical (FRUIT_OMP_DEALLOCATE_MESSAGE_ARRAY)
  end subroutine testsuite_finalize

  subroutine testsuite_initialize_xml(rank)
    !! category: testsuite subroutine
    !! Initialize FRUIT driver environment for output to XML file
    integer, optional, intent(in) :: rank
    logical :: rank_zero_or_single

    rank_zero_or_single = .true.
    if (present(rank)) then
      if (rank /= 0) then
        rank_zero_or_single = .false.
      endif
    endif

    if (rank_zero_or_single) then
      open (XML_OPEN, file=xml_filename, action="write", status="replace")
      write (XML_OPEN, '("<?xml version=""1.0"" encoding=""UTF-8""?>")')
      write (XML_OPEN, '("<testsuites>")')
      write (XML_OPEN, '("  <testsuite ")', advance="no")
      write (XML_OPEN, '(      "errors=""0"" "   )', advance="no")
      write (XML_OPEN, '(      "tests=""1"" "    )', advance="no")
      write (XML_OPEN, '(      "failures=""1"" " )', advance="no")
      write (XML_OPEN, '(      "name=""", a, """ ")', advance="no") "name of test suite"
      write (XML_OPEN, '(      "id=""1"">")')

      write (XML_OPEN, &
        &  '("    <testcase name=""", a, """ classname=""", a, """ time=""", a, """>")') &
        &  "dummy_testcase", "dummy_classname", "0"

      write (XML_OPEN, '(a)', advance="no") "      <failure type=""failure"" message="""
      write (XML_OPEN, '(a)', advance="no") "FRUIT did not generate regular content of result.xml."
      write (XML_OPEN, '(a)') """/>"
      write (XML_OPEN, '("    </testcase>")')

      write (XML_OPEN, '("  </testsuite>")')
      write (XML_OPEN, '("</testsuites>")')
      close (XML_OPEN)
    endif

    open (xml_work, FILE=xml_filename_work, action="write", status='replace')
    close (xml_work)
  end subroutine testsuite_initialize_xml

  function case_delta_t()
    character(len=STRLEN_T) :: case_delta_t
    real :: delta_t
    integer :: case_time_to, time_rate, time_max

    call system_clock(case_time_to, time_rate, time_max)
    if (time_rate > 0) then
      delta_t = real(case_time_to - case_time_from)/real(time_rate)
      if (delta_t < 0) then
        delta_t = delta_t + real(time_max)/real(time_rate)
      endif
    else
      delta_t = 0
    endif

    write (case_delta_t, '(g12.4)') delta_t
    case_delta_t = adjustl(case_delta_t)
  end function case_delta_t

  subroutine case_passed_xml(tc_name, classname)
    !! category: testsuite subroutine
    !! Write to XML file a passed case.
    character(*), intent(in) :: tc_name
    character(*), intent(in) :: classname
    character(len=STRLEN_T) :: case_time

    case_time = case_delta_t()

    open (xml_work, FILE=xml_filename_work, position='append')
    write (xml_work, &
      &  '("    <testcase name=""", a, """ classname=""", a, a, """ time=""", a, """/>")') &
      &  trim(tc_name), trim(prefix), trim(classname), trim(case_time)
    close (xml_work)
  end subroutine case_passed_xml

  subroutine case_failed_xml(tc_name, classname)
    !! category: testsuite subroutine
    !! Write to XML file a passed case.
    character(*), intent(in) :: tc_name
    character(*), intent(in) :: classname
    integer :: i, j
    character(len=STRLEN_T) :: case_time

    case_time = case_delta_t()

    open (xml_work, FILE=xml_filename_work, position='append')
    write (xml_work, &
      &  '("    <testcase name=""", a, """ classname=""", a, a, """ time=""", a, """>")') &
      &  trim(tc_name), trim(prefix), trim(classname), trim(case_time)

    write (xml_work, '("      <failure type=""failure"" message=""")', advance="no")

    do i = message_index_from, message_index - 1
      j = i - message_index_from + 1
      if (j > MAX_NUM_FAILURES_IN_XML) then
        write (xml_work, '("(omit the rest)")', advance="no")
        exit
      endif

      write (xml_work, '(a)', advance="no") trim(adjustl(message_array(i)))

      if (i == message_index - 1) then
        continue
      else
        write (xml_work, '("&#xA;")', advance="no")
      endif
    enddo
    write (xml_work, '("""/>")')

    write (xml_work, &
      &  '("    </testcase>")')
    close (xml_work)
  end subroutine case_failed_xml

  subroutine testsuite_summary_xml
    !! category: testsuite subroutine
    !! Summarize FRUIT test results in XML format to result.xml file.
    character(len=XML_LINE_LENGTH) :: whole_line
    character(len=100) :: full_count
    character(len=100) :: fail_count

    full_count = int_to_str(successful_case_count + failed_case_count)
    fail_count = int_to_str(failed_case_count)

    open (XML_OPEN, file=xml_filename, action="write", status="replace")
    write (XML_OPEN, '("<?xml version=""1.0"" encoding=""UTF-8""?>")')
    write (XML_OPEN, '("<testsuites>")')
    write (XML_OPEN, '("  <testsuite errors=""0"" ")', advance="no")
    write (XML_OPEN, '("tests=""", a, """ ")', advance="no") &
      &  trim(full_count)
    write (XML_OPEN, '("failures=""", a, """ ")', advance="no") &
      &  trim(fail_count)
    write (XML_OPEN, '("name=""", a, """ ")', advance="no") &
      &  "name of test suite"
    write (XML_OPEN, '("id=""1"">")')

    open (xml_work, FILE=xml_filename_work)
    do
      read (xml_work, '(a)', end=999) whole_line
      write (XML_OPEN, '(a)') trim(whole_line)
    enddo
    999 continue
    close (xml_work)

    write (XML_OPEN, '("  </testsuite>")')
    write (XML_OPEN, '("</testsuites>")')
    close (XML_OPEN)
  end subroutine testsuite_summary_xml

  function int_to_str(i)
    integer, intent(in) :: i
    character(LEN=NUMBER_LENGTH) :: int_to_str

    write (int_to_str, '(i10)') i
    int_to_str = adjustl(int_to_str)
  end function int_to_str

  logical function fruit_if_case_failed()
    !! category: testsuite subroutine
    !! Return TRUE if any assert in current case has failed.
    if (failed_assert_count == 0) then
      fruit_if_case_failed = .false.
      return
    endif

    if (case_passed) then
      fruit_if_case_failed = .false.
    else
      fruit_if_case_failed = .true.
    endif
  end function fruit_if_case_failed

  subroutine fruit_show_dots
    !! category: testsuite subroutine
    !! Show dots signifying test success on screen. Visible by default.
    if_show_dots = .true.
  end subroutine fruit_show_dots

  subroutine fruit_hide_dots
    !! category: testsuite subroutine
    !! Hide dots signifying test success on screen. Visible by default.
    if_show_dots = .false.
  end subroutine fruit_hide_dots

  subroutine testcase_initialize(tc_name)
    !! category: testcase subroutine
    !! summary: Initialize a testcase.
    !! Initialize a test case.<br/><br/>
    character(*), intent(in), optional :: tc_name

    initial_failed_assert_count = failed_assert_count

    ! Set the name of the test case
    if (present(tc_name)) then
      call set_case_name(tc_name)
    else
      call set_case_name('unnamed')
    endif

    last_passed = .true.
    case_passed = .true.
    linechar_count = 0  ! reset linechar_count for each test case.
    message_index_from = message_index
    call system_clock(case_time_from)

    !$OMP BARRIER
    ! "case_passed" is true here.
    ! "case_passed" becomes .false. at the first fail of assertion
  end subroutine testcase_initialize

  subroutine testcase_finalize(exit_code)
    !! category: testcase subroutine
    !! summary: Finalize a testcase
    !! Finalize a testcase and optionally 
    !! return no. of failed asserts as an *exit_code*.
    !! Initialize a test case.<br/><br/>
    integer, intent(out), optional :: exit_code

    !$OMP BARRIER
    if (initial_failed_assert_count .eq. failed_assert_count) then
      ! If no additional assertions failed during the run of this test case
      ! then the test case was successful
      successful_case_count = successful_case_count + 1
    else
      failed_case_count = failed_case_count + 1
    end if

    testCaseIndex = testCaseIndex + 1
    if (present(exit_code)) &
      & exit_code = failed_assert_count - initial_failed_assert_count

    ! Reset the name of the unit test back to the default
    call set_case_name(DEFAULT_CASE_NAME)

  end subroutine testcase_finalize

  subroutine testsuite_summary()
    !! category: testsuite subroutine
    !! Summarize FRUIT test results to screen.
    integer :: i

    write (stdout, *)
    write (stdout, *)
    write (stdout, *) '    Start of FRUIT summary: '
    write (stdout, *)

    if (failed_assert_count > 0) then
      write (stdout, *) 'Some tests failed!'
    else
      write (stdout, *) 'SUCCESSFUL!'
    end if

    write (stdout, *)
    if (message_index > 1) then
      write (stdout, *) '  -- Failed assertion messages:'

      do i = 1, message_index - 1
        write (stdout, "(A)") '   '//trim(adjustl(message_array(i)))
      end do

      write (stdout, *) '  -- end of failed assertion messages.'
      write (stdout, *)
    else
      write (stdout, *) '  No messages '
    end if

    if (successful_assert_count + failed_assert_count /= 0) then
      ! If testcase not intialized using testcase_intialize()
      if (successful_case_count + failed_case_count == 0) then
        failed_case_count = min(1, failed_assert_count)
        if (failed_case_count == 0) successful_case_count = 1
      endif
      call testsuite_summary_table(&
        & successful_assert_count, failed_assert_count, &
        & successful_case_count, failed_case_count &
        &)
    end if
    write (stdout, *) '  -- end of FRUIT summary'
  end subroutine testsuite_summary

  subroutine testsuite_summary_table(&
      & succ_assert, fail_assert, &
      & succ_case, fail_case    &
      &)
    !! category: testsuite subroutine
    !! Print statistics of cases and asserts in default format.
    integer, intent(in) :: succ_assert, fail_assert
    integer, intent(in) :: succ_case, fail_case

    write (stdout, *) 'Total asserts :   ', succ_assert + fail_assert
    write (stdout, *) 'Successful    :   ', succ_assert
    write (stdout, *) 'Failed        :   ', fail_assert
    write (stdout, '("Successful rate:   ",f6.2,"%")') real(succ_assert)*100.0/ &
      real(succ_assert + fail_assert)
    write (stdout, *)
    write (stdout, *) 'Successful asserts / total asserts : [ ', &
      succ_assert, '/', succ_assert + fail_assert, ' ]'
    write (stdout, *) &
      & 'Successful cases   / total cases   : [ ', succ_case, '/', &
      succ_case + fail_case, ' ]'
  end subroutine testsuite_summary_table

  subroutine add_fail_(message)
    !! category: testsuite subroutine
    !! summary: Print message to screen on assert failure and add to count.
    !! Print message to screen on assert failure and add to count.
    character(*), intent(in), optional :: message
    call failed_assert_action('none', 'none', message, if_is=.true.)
  end subroutine add_fail_

  subroutine add_fail_case_named_(caseName, message)
    !! category: testsuite subroutine
    !! summary: Print message to screen on assert failure and add to count.
    !! Print message to screen on assert failure and add to count.
    character(*), intent(in) :: caseName
    character(*), intent(in) :: message

    call add_fail_("[in "//caseName//"(fail)]: "//message)
  end subroutine add_fail_case_named_

  subroutine is_all_successful(result)
    !! category: testsuite subroutine
    !! Return true to *result* if any assert has failed till now.
    logical, intent(out) :: result
    result = (failed_assert_count .eq. 0)
  end subroutine is_all_successful

  ! Private, helper routine to wrap lines of success/failed marks
  subroutine output_mark_(chr)
    !! Wrap lines of success/failed marks
    character(1), intent(in) :: chr
    !  integer, save :: linechar_count = 0
    !  Definition of linechar_count is moved to module,
    !  so that it can be stashed and restored.

    !$omp critical      (FRUIT_OMP_ADD_OUTPUT_MARK)
    linechar_count = linechar_count + 1
    if (linechar_count .lt. MAX_MARKS_PER_LINE) then
      write (stdout, "(A1)", ADVANCE='NO') chr
    else
      write (stdout, "(A1)", ADVANCE='YES') chr
      linechar_count = 0
    endif
    !$omp end critical  (FRUIT_OMP_ADD_OUTPUT_MARK)
  end subroutine output_mark_

  subroutine success_mark_
    !! category: testsuite subroutine
    !! Print success mark
    call output_mark_('.')
  end subroutine success_mark_

  subroutine failed_mark_
    !! category: testsuite subroutine
    !! Print failed mark
    call output_mark_('F')
  end subroutine failed_mark_

  subroutine increase_message_stack_
    !! Increase message stack size
    character(len=MSG_LENGTH) :: msg_swap_holder(current_max)

    ! If testsuite_initialize hasn't been called
    !$omp critical (FRUIT_OMP_ALLOCATE_MESSAGE_ARRAY)
    if (.not. allocated(message_array)) then
      allocate (message_array(MSG_ARRAY_INCREMENT))
    end if
    !$omp end critical (FRUIT_OMP_ALLOCATE_MESSAGE_ARRAY)

    if (message_index > MAX_MSG_STACK_SIZE) then
      return
    end if

    if (message_index > current_max) then
      msg_swap_holder(1:current_max) = message_array(1:current_max)
      deallocate (message_array)
      current_max = current_max + MSG_ARRAY_INCREMENT
      allocate (message_array(current_max))
      message_array(1:current_max - MSG_ARRAY_INCREMENT) &
        = msg_swap_holder(1:current_max - MSG_ARRAY_INCREMENT)
    end if

    message_array(message_index) = msg
    if (message_index == MAX_MSG_STACK_SIZE) then
      message_array(message_index) = "Max number of messages reached. Further messages suppressed."
    endif

    message_index = message_index + 1

    if (message_index > MAX_MSG_STACK_SIZE) then
      write (stdout, *) "Stop because there are too many error messages to put into stack."
      write (stdout, *) "Try to increase MAX_MSG_STACK_SIZE if you really need so."
    end if
  end subroutine increase_message_stack_

  subroutine get_xml_filename_work(string)
    !! category: testsuite subroutine
    !! Get filename of XML file. result.xml by default.
    character(len=*), intent(out) :: string
    string = trim(xml_filename_work)
  end subroutine get_xml_filename_work

  subroutine set_xml_filename_work(string)
    !! category: testsuite subroutine
    !! Set filename of XML file. result.xml by default.
    character(len=*), intent(in) :: string
    xml_filename_work = trim(string)
  end subroutine set_xml_filename_work

  function get_last_message()
    !! category: testsuite subroutine
    !! Return last message.
    character(len=MSG_LENGTH) :: get_last_message
    if (message_index > 1) then
      get_last_message = trim(adjustl(message_array(message_index - 1)))
    else
      get_last_message = ''
    end if
  end function get_last_message

  subroutine get_message_index(index)
    !! category: testsuite subroutine
    !! Get number of failed assertion messages.
    integer, intent(out) :: index

    index = message_index
  end subroutine get_message_index

  subroutine get_message_array(msgs)
    !! category: testsuite subroutine
    !! Get failed asssertion messages to *msgs*.
    character(len=*), intent(out) :: msgs(:)
    integer :: i
    msgs(:) = ""

    do i = 1, message_index - 1
      msgs(i) = trim(adjustl(message_array(i)))
    enddo
  end subroutine get_message_array

  subroutine get_messages(msgs)
    !! category: testsuite subroutine
    !! Get failed asssertion messages to *msgs*.
    character(len=*), intent(out) :: msgs(:)
    integer :: i, j

    msgs(:) = ""
    do i = message_index_from, message_index - 1
      j = i - message_index_from + 1
      if (j > ubound(msgs, 1)) exit
      msgs(j) = trim(adjustl(message_array(i)))
    enddo
  end subroutine get_messages

  subroutine get_total_count(count)
    !! category: testsuite subroutine
    !! Get total number of asserts.
    integer, intent(out) :: count

    count = successful_assert_count + failed_assert_count
  end subroutine get_total_count

  subroutine get_failed_count(count)
    !! category: testsuite subroutine
    !! Get number of assert failures.
    integer, intent(out) :: count
    count = failed_assert_count
  end subroutine get_failed_count

  subroutine add_success
    !! category: testsuite subroutine
    !! summary: Print message to screen on assert success and add to count.
    !! Print message to screen on assert success and add to count.
    !$omp critical     (FRUIT_OMP_ADD_SUCCESS)
    successful_assert_count = successful_assert_count + 1
    last_passed = .true.
    !$omp end critical (FRUIT_OMP_ADD_SUCCESS)

    if (if_show_dots) then
      call success_mark_
    endif
  end subroutine add_success

  subroutine failed_assert_action(expected, got, message, if_is)
    !! category: testsuite subroutine
    !! Print *message* to screen and take necessary actions for assert failure.
    character(*), intent(in) :: expected, got
    character(*), intent(in), optional :: message
    logical, intent(in), optional :: if_is

    !$omp critical     (FRUIT_OMP_ADD_FAIL)
    if (present(if_is)) then
      call make_error_msg_(expected, got, if_is, message)
    else
      call make_error_msg_(expected, got, .true., message)
    endif
    call increase_message_stack_
    failed_assert_count = failed_assert_count + 1
    last_passed = .false.
    case_passed = .false.
    !$omp end critical (FRUIT_OMP_ADD_FAIL)
    call failed_mark_
  end subroutine failed_assert_action

  subroutine set_case_name(value)
    !! category: testsuite subroutine
    !! Set name of case to *value*.
    character(*), intent(in) :: value
    case_name = trim(adjustl(value))
  end subroutine set_case_name

  subroutine get_case_name(value)
    !! category: testsuite subroutine
    !! Get name of case to *value*.
    character(*), intent(out) :: value
    value = trim(adjustl(case_name))
  end subroutine get_case_name

  subroutine make_error_msg_(var1, var2, if_is, message)
    character(*), intent(in) :: var1, var2
    logical, intent(in)           :: if_is
    character(*), intent(in), optional :: message

    msg = '['//trim(adjustl(case_name))//']:'
    if (if_is) then
      msg = trim(msg)//' Expected'
    else
      msg = trim(msg)//' Expected Not'
    endif
    msg = trim(msg)//' ['//trim(adjustl(var1))//'],'
    msg = trim(msg)//' Got'
    msg = trim(msg)//' ['//trim(adjustl(var2))//']'

    if (present(message)) then
      msg = trim(msg)//'; User message: ['//trim(message)//']'
    endif
  end subroutine make_error_msg_

  function is_last_passed()
    !! category: testsuite subroutine
    !! Return true if last assert is successful in case.
    logical:: is_last_passed
    is_last_passed = last_passed
  end function is_last_passed

  function is_case_passed()
    !! category: testsuite subroutine
    !! Return true if all asserts are successful in case.
    logical:: is_case_passed
    is_case_passed = case_passed
  end function is_case_passed

  subroutine override_stdout(write_unit, filename)
    !! category: testsuite subroutine
    !! Override stdout to a user-specified file. Terminal by default.
    integer, intent(in) ::    write_unit
    character(len=*), intent(in) :: filename

    stdout = write_unit
    open (stdout, file=filename, action="write", status="replace")
  end subroutine override_stdout

  subroutine override_xml_work(new_unit, filename)
    !! category: testsuite subroutine
    !! Override XML file unit number to a user-specified number. 21 by default.
    integer, intent(in) ::    new_unit
    character(len=*), intent(in) :: filename

    xml_work = new_unit
    xml_filename_work = filename
    open (xml_work, file=filename, action="write", status="replace")
  end subroutine override_xml_work

  subroutine stash_test_suite
    !! category: testsuite subroutine
    !! Stash results of test case for later use.
    stashed_suite%successful_assert_count = successful_assert_count
    successful_assert_count = 0

    stashed_suite%failed_assert_count = failed_assert_count
    failed_assert_count = 0

    allocate (stashed_suite%message_array(current_max))
    stashed_suite%message_array(1:message_index) = &
      & message_array(1:message_index)
    deallocate (message_array)
    allocate (message_array(MSG_ARRAY_INCREMENT))

    stashed_suite%message_index = message_index
    message_index = 1
    stashed_suite%message_index_from = message_index_from
    message_index_from = 1

    stashed_suite%current_max = current_max
    current_max = 50
    stashed_suite%successful_case_count = successful_case_count
    successful_case_count = 0
    stashed_suite%failed_case_count = failed_case_count
    failed_case_count = 0
    stashed_suite%testCaseIndex = testCaseIndex
    testCaseIndex = 1
    stashed_suite%case_name = case_name
    case_name = DEFAULT_CASE_NAME

    stashed_suite%last_passed = last_passed
    last_passed = .false.
    stashed_suite%case_passed = case_passed
    case_passed = DEFAULT_CASE_PASSED
    stashed_suite%case_time_from = case_time_from
    case_time_from = 0
    stashed_suite%linechar_count = linechar_count
    linechar_count = 0
    stashed_suite%if_show_dots = if_show_dots
    if_show_dots = .true.
  end subroutine stash_test_suite

  subroutine restore_test_suite
    !! category: testsuite subroutine
    !! Restore results of test case for use.
    successful_assert_count = stashed_suite%successful_assert_count
    failed_assert_count = stashed_suite%failed_assert_count

    message_index = stashed_suite%message_index
    message_index_from = stashed_suite%message_index_from
    current_max = stashed_suite%current_max

    deallocate (message_array)
    allocate (message_array(current_max))
    message_array(1:message_index) = &
      & stashed_suite%message_array(1:message_index)
    deallocate (stashed_suite%message_array)

    successful_case_count = stashed_suite%successful_case_count
    failed_case_count = stashed_suite%failed_case_count
    testCaseIndex = stashed_suite%testCaseIndex

    case_name = stashed_suite%case_name
    last_passed = stashed_suite%last_passed
    case_passed = stashed_suite%case_passed
    case_time_from = stashed_suite%case_time_from
    linechar_count = stashed_suite%linechar_count
    if_show_dots = stashed_suite%if_show_dots
  end subroutine restore_test_suite

  subroutine end_override_stdout()
    !! category: testsuite subroutine
    !! Revert override of stdout to default. Terminal by default.
    close (stdout)
    stdout = STDOUT_DEFAULT
  end subroutine end_override_stdout

  subroutine end_override_xml_work()
    !! category: testsuite subroutine
    !! Revert override of XML file unit number to default. 21 by default.
    close (xml_work)
    xml_work = XML_WORK_DEFAULT
    xml_filename_work = XML_FN_WORK_DEF
  end subroutine end_override_xml_work

  subroutine set_prefix(str)
    !! category: testsuite subroutine
    !! Set a common prefix for classname. Null by default.
    character(len=*), intent(in) :: str
    character(len=len_trim(str)) :: str2

    str2 = trim(adjustl(str))
    if (len_trim(str2) <= FRUIT_PREFIX_LEN_MAX) then
      prefix = str2
    else
      prefix = str2(1:FRUIT_PREFIX_LEN_MAX)
    endif
  end subroutine set_prefix

  subroutine get_prefix(str)
    !! category: testsuite subroutine
    !! Get a common prefix for classname. Null by default.
    character(len=*), intent(out) :: str

    if (len(str) <= len(prefix)) then
      str = trim(prefix)
    else
      str = prefix
    endif
  end subroutine get_prefix

  subroutine get_assert_and_case_count(fail_assert, suc_assert, fail_case, suc_case)
    !! category: testsuite subroutine
    !! Get statistics of cases and asserts.
    integer, intent(out) :: fail_assert, suc_assert, fail_case, suc_case

    fail_assert = failed_assert_count
    suc_assert = successful_assert_count
    fail_case = failed_case_count
    suc_case = successful_case_count
  end subroutine get_assert_and_case_count

  !--------------------------------------------------------------------------------
  ! all assertions
  !--------------------------------------------------------------------------------
  subroutine assert_true(var1, message, status)
    !! category: testcase subroutine
    !! Test that *var1* is true.
    logical, intent(in) :: var1
    character(*), intent(in), optional :: message
    logical, intent(out), optional :: status

    if (var1 .eqv. .true.) then
      if (.not. present(status)) then
        call add_success
      else
        status = .true.
      endif
    else
      if (.not. present(status)) then
        call failed_assert_action(to_s(.true.), to_s(var1), message, if_is=.true.)
      else
        status = .false.
      endif
    end if
  end subroutine assert_true

  subroutine assert_false(var1, message, status)
    !! category: testcase subroutine
    !! Test that *var1* is false.
    logical, intent(in) :: var1
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status

    if (var1 .eqv. .false.) then
      if (.not. present(status)) then
        call add_success
      else
        status = .true.
      endif
    else
      if (.not. present(status)) then
        call failed_assert_action(to_s(.true.), to_s(var1), message, if_is=.false.)
      else
        status = .false.
      endif
    endif
  end subroutine assert_false

  !====== begin of generated code ======
  !------ 0d_logical ------
  subroutine assert_eq_logical_(var1, var2, message, status)
    logical, intent(in) :: var1, var2
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status

    if (var1 .neqv. var2) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1), &
          & to_s(var2), message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_eq_logical_

  !------ 1d_logical ------
  subroutine assert_eq_1d_logical_(var1, var2, message, status)
    logical, intent(in), dimension(:) :: var1, var2
    integer :: n
    integer, dimension(1) :: indx
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical, dimension(size(var1, 1)) :: logical_array

    n = size(var1, 1)

    if (n .ne. size(var2, 1)) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(n), &
          & to_s(size(var2, 1)), &
          & '1d arrays have different sizes, '//message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    logical_array = (var1 .eqv. var2)
    if (all(logical_array)) then
      if (.not. present(status)) then
        call add_success
      else
        status = .true.
      endif
    else
      indx = findfalse(logical_array)
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(indx(1))), &
          & to_s(var2(indx(1))), &
          & '1d array has difference, '//message, if_is=.true.)
      else
        status = .false.
      endif
    endif

  end subroutine assert_eq_1d_logical_

  !------ 2d_logical ------
  subroutine assert_eq_2d_logical_(var1, var2, message, status)
    logical, intent(in), dimension(:, :) :: var1, var2
    integer :: n, m
    integer, dimension(2) :: indx
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical, dimension(size(var1, 1), size(var1, 2)) :: logical_array

    n = size(var1, 1)
    m = size(var1, 2)

    if ((size(var2, 1) .ne. n) .and. (size(var2, 2) .ne. m)) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(n)//' x '//to_s(m), &
          & to_s(size(var2, 1))//' x '//to_s(size(var2, 1)), &
          & '2d arrays have different sizes, '//message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    logical_array = (var1 .eqv. var2)
    if (all(logical_array)) then
      if (.not. present(status)) then
        call add_success
      else
        status = .true.
      endif
    else
      indx = findfalse(logical_array)
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(indx(1), indx(2))), &
          & to_s(var2(indx(1), indx(2))), &
          & '2d array has difference, '//message, if_is=.true.)
      else
        status = .false.
      endif
    endif
  end subroutine assert_eq_2d_logical_

  !------ 0d_string ------
  subroutine assert_eq_string_(var1, var2, message, status)
    character(len=*), intent(in) :: var1, var2
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status

    if (adjustl(var1) /= adjustl(var2)) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1), &
          & to_s(var2), message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_eq_string_

  !------ 1d_string ------
  subroutine assert_eq_1d_string_(var1, var2, message, status)
    character(len=*), intent(in), dimension(:) :: var1, var2
    integer :: i, n
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status

    n = size(var1, 1)

    if (n .ne. size(var2, 1)) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(n), &
          & to_s(size(var2, 1)), &
          & '1d arrays have different sizes, '//message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    do i = 1, n
      if (adjustl(var1(i)) /= adjustl(var2(i))) then
        if (.not. present(status)) then
          call failed_assert_action( &
            & to_s(var1(i)), &
            & to_s(var2(i)), &
            & '1d array has difference, '//message, if_is=.true.)
        else
          status = .false.
        endif
        return
      endif
    enddo
    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_eq_1d_string_

  !------ 2d_string ------
  subroutine assert_eq_2d_string_(var1, var2, message, status)
    character(len=*), intent(in), dimension(:, :) :: var1, var2
    integer :: i, j, n, m
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status

    n = size(var1, 1)
    m = size(var1, 2)

    if ((size(var2, 1) .ne. n) .and. (size(var2, 2) .ne. m)) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(n)//' x '//to_s(m), &
          & to_s(size(var2, 1))//' x '//to_s(size(var2, 1)), &
          & '2d arrays have different sizes, '//message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    do j = 1, m
      do i = 1, n
        if (adjustl(var1(i, j)) /= adjustl(var2(i, j))) then
          if (.not. present(status)) then
            call failed_assert_action( &
              & to_s(var1(i, j)), &
              & to_s(var2(i, j)), '2d array has difference, '//message, if_is=.true.)
          else
            status = .false.
          endif
          return
        endif
      enddo
    enddo
    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_eq_2d_string_

  !------ 0d_int ------
  subroutine assert_eq_int_(var1, var2, message, status)
    integer, intent(in) :: var1, var2
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status

    if (var1 /= var2) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1), &
          & to_s(var2), message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_eq_int_

  !------ 1d_int ------
  subroutine assert_eq_1d_int_(var1, var2, message, status)
    integer, intent(in), dimension(:) :: var1, var2
    integer :: n
    integer, dimension(1) :: indx
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical, dimension(size(var1, 1)) :: logical_array

    n = size(var1, 1)

    if (n .ne. size(var2, 1)) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(n), &
          & to_s(size(var2, 1)), &
          & '1d arrays have different sizes, '//message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    logical_array = (var1 == var2)
    if (all(logical_array)) then
      if (.not. present(status)) then
        call add_success
      else
        status = .true.
      endif
    else
      indx = findfalse(logical_array)
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(indx(1))), &
          & to_s(var2(indx(1))), &
          & '1d array has difference, '//message, if_is=.true.)
      else
        status = .false.
      endif
    endif
  end subroutine assert_eq_1d_int_

  !------ 2d_int ------
  subroutine assert_eq_2d_int_(var1, var2, message, status)
    integer, intent(in), dimension(:, :) :: var1, var2
    integer :: n, m
    integer, dimension(2) :: indx
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical, dimension(size(var1, 1), size(var1, 2)) :: logical_array

    n = size(var1, 1)
    m = size(var1, 2)

    if ((size(var2, 1) .ne. n) .and. (size(var2, 2) .ne. m)) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(n)//' x '//to_s(m), &
          & to_s(size(var2, 1))//' x '//to_s(size(var2, 1)), &
          & '2d arrays have different sizes, '//message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    logical_array = (var1 == var2)
    if (all(logical_array)) then
      if (.not. present(status)) then
        call add_success
      else
        status = .true.
      endif
    else
      indx = findfalse(logical_array)
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(indx(1), indx(2))), &
          & to_s(var2(indx(1), indx(2))), &
          & '2d array has difference, '//message, if_is=.true.)
      else
        status = .false.
      endif
    endif
  end subroutine assert_eq_2d_int_

  !------ 0d_real ------
  subroutine assert_eq_real_(var1, var2, delta, message, status)
    real, intent(in) :: var1, var2
    real, intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    real :: tol

    tol = eps
    if (present(delta)) tol = delta

    if (abs(var1 - var2) > tol) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1), &
          & to_s(var2), message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_eq_real_

  !------ 1d_real ------
  subroutine assert_eq_1d_real_(var1, var2, delta, message, status)
    real, intent(in), dimension(:) :: var1, var2
    real, intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    integer :: n
    integer, dimension(1) :: indx
    logical, dimension(size(var1, 1)) :: logical_array
    real :: tol

    n = size(var1, 1)

    if (n .ne. size(var2, 1)) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(n), &
          & to_s(size(var2, 1)), &
          & '1d arrays have different sizes, '//message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    tol = eps
    if (present(delta)) tol = delta

    logical_array = (abs(var1 - var2) <= tol)
    if (all(logical_array)) then
      if (.not. present(status)) then
        call add_success
      else
        status = .true.
      endif
    else
      indx = findfalse(logical_array)
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(indx(1))), &
          & to_s(var2(indx(1))), &
          & '1d array has difference, '//message, if_is=.true.)
      else
        status = .false.
      endif
    endif
  end subroutine assert_eq_1d_real_

  !------ 2d_real ------
  subroutine assert_eq_2d_real_(var1, var2, delta, message, status)
    integer :: n, m
    integer, dimension(2) :: indx
    real, intent(in), dimension(:, :) :: var1, var2
    real, intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    real :: tol
    logical, dimension(size(var1, 1), size(var1, 2)) :: logical_array

    n = size(var1, 1)
    m = size(var1, 2)

    if ((size(var2, 1) .ne. n) .and. (size(var2, 2) .ne. m)) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(n)//' x '//to_s(m), &
          & to_s(size(var2, 1))//' x '//to_s(size(var2, 1)), &
          & '2d arrays have different sizes, '//message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    tol = eps
    if (present(delta)) tol = delta

    logical_array = (abs(var1 - var2) <= tol)
    if (all(logical_array)) then
      if (.not. present(status)) then
        call add_success
      else
        status = .true.
      endif
    else
      indx = findfalse(logical_array)
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(indx(1), indx(2))), &
          & to_s(var2(indx(1), indx(2))), &
          & '2d array has difference, '//message, if_is=.true.)
      else
        status = .false.
      endif
    endif
  end subroutine assert_eq_2d_real_

  !------ 0d_double ------
  subroutine assert_eq_double_(var1, var2, delta, message, status)
    real(dp), intent(in) :: var1, var2
    real(dp), intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    real(dp) :: tol

    tol = eps_dp
    if (present(delta)) tol = delta

    if (abs(var1 - var2) > tol) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1), &
          & to_s(var2), message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_eq_double_

  !------ 1d_double ------
  subroutine assert_eq_1d_double_(var1, var2, delta, message, status)
    integer :: n
    integer, dimension(1) :: indx
    real(dp), intent(in), dimension(:) :: var1, var2
    real(dp), intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical, dimension(size(var1, 1)) :: logical_array
    real(dp) :: tol

    n = size(var1, 1)

    if (n .ne. size(var2, 1)) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(n), &
          & to_s(size(var2, 1)), &
          & '1d arrays have different sizes, '//message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    tol = eps_dp
    if (present(delta)) tol = delta

    logical_array = (abs(var1 - var2) <= tol)
    if (all(logical_array)) then
      if (.not. present(status)) then
        call add_success
      else
        status = .true.
      endif
    else
      indx = findfalse(logical_array)
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(indx(1))), &
          & to_s(var2(indx(1))), &
          & '1d array has difference, '//message, if_is=.true.)
      else
        status = .false.
      endif
    endif

  end subroutine assert_eq_1d_double_

  !------ 2d_double ------
  subroutine assert_eq_2d_double_(var1, var2, delta, message, status)
    integer :: n, m
    integer, dimension(2) :: indx
    real(dp), intent(in), dimension(:, :) :: var1, var2
    real(dp), intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical, dimension(size(var1, 1), size(var1, 2)) :: logical_array
    real(dp) :: tol

    n = size(var1, 1)
    m = size(var1, 2)

    if ((size(var2, 1) .ne. n) .and. (size(var2, 2) .ne. m)) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(n)//' x '//to_s(m), &
          & to_s(size(var2, 1))//' x '//to_s(size(var2, 1)), &
          & '2d arrays have different sizes, '//message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    tol = eps_dp
    if (present(delta)) tol = delta

    logical_array = (abs(var1 - var2) <= tol)
    if (all(logical_array)) then
      if (.not. present(status)) then
        call add_success
      else
        status = .true.
      endif
    else
      indx = findfalse(logical_array)
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(indx(1), indx(2))), &
          & to_s(var2(indx(1), indx(2))), &
          & '2d array has difference, '//message, if_is=.true.)
      else
        status = .false.
      endif
    endif
  end subroutine assert_eq_2d_double_

  !------ 0d_complex_real ------
  subroutine assert_eq_complex_real_(var1, var2, delta, message, status)
    complex, intent(in) :: var1, var2
    real, intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    real :: tol

    tol = eps
    if (present(delta)) tol = delta

    if (abs(real(var1-var2)) > tol .or. abs(aimag(var1-var2)) > tol) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1), &
          & to_s(var2), message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_eq_complex_real_

  !------ 1d_complex_real ------
  subroutine assert_eq_1d_complex_real_(var1, var2, delta, message, status)
    integer :: i, n
    complex, intent(in), dimension(:) :: var1, var2
    real, intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    real :: tol

    n = size(var1, 1)

    if (n .ne. size(var2, 1)) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(n), &
          & to_s(size(var2, 1)), '1d arrays have different sizes, '//message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    tol = eps
    if (present(delta)) tol = delta

    do i = 1, n
      if (abs(real(var1(i) - var2(i))) > tol .or. &
        abs(aimag(var1(i) - var2(i))) > tol) then
        if (.not. present(status)) then
          call failed_assert_action( &
            & to_s(var1(i)), &
            & to_s(var2(i)), '1d array has difference, '//message, if_is=.true.)
        else
          status = .false.
        endif
        return
      endif
    enddo
    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_eq_1d_complex_real_

  !------ 2d_complex_real ------
  subroutine assert_eq_2d_complex_real_(var1, var2, delta, message, status)
    integer :: i, j, n, m
    complex, intent(in), dimension(:, :) :: var1, var2
    real, intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    real :: tol

    n = size(var1, 1)
    m = size(var1, 2)

    if ((size(var2, 1) .ne. n) .and. (size(var2, 2) .ne. m)) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(n)//' x '//to_s(m), &
          & to_s(size(var2, 1))//' x '//to_s(size(var2, 1)), &
          & '2d arrays have different sizes, '//message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    tol = eps
    if (present(delta)) tol = delta

    do j = 1, m
      do i = 1, n
        if (abs(real(var1(i, j) - var2(i, j))) > tol .or. &
          abs(aimag(var1(i, j) - var2(i, j))) > tol ) then
          if (.not. present(status)) then
            call failed_assert_action( &
              & to_s(var1(i, j)), &
              & to_s(var2(i, j)), '2d array has difference, '//message, if_is=.true.)
          else
            status = .false.
          endif
          return
        endif
      enddo
    enddo
    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_eq_2d_complex_real_

  !------ 0d_complex_double ------
  subroutine assert_eq_complex_double_(var1, var2, delta, message, status)
    complex(dp), intent(in) :: var1, var2
    real(dp), intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    real(dp) :: tol

    tol = eps_dp
    if (present(delta)) tol = delta

    if (abs(real(var1 - var2, kind=dp)) > tol .or. &
      abs(dimag(var1 - var2)) > tol) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1), &
          & to_s(var2), message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_eq_complex_double_

  !------ 1d_complex_double ------
  subroutine assert_eq_1d_complex_double_(var1, var2, delta, message, status)
    integer :: i, n
    complex(dp), intent(in), dimension(:) :: var1, var2
    real(dp), intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    real(dp) :: tol

    n = size(var1, 1)

    if (n .ne. size(var2, 1)) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(n), &
          & to_s(size(var2, 1)), '1d arrays have different sizes, '//message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    tol = eps_dp
    if (present(delta)) tol = delta

    do i = 1, n
      if (abs(real(var1(i) - var2(i), kind=dp)) > tol .or. &
        abs(dimag(var1(i) - var2(i))) > tol) then
        if (.not. present(status)) then
          call failed_assert_action( &
            & to_s(var1(i)), &
            & to_s(var2(i)), '1d array has difference, '//message, if_is=.true.)
        else
          status = .false.
        endif
        return
      endif
    enddo
    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_eq_1d_complex_double_

  !------ 2d_complex_double ------
  subroutine assert_eq_2d_complex_double_(var1, var2, delta, message, status)
    integer :: i, j, n, m
    complex(dp), intent(in), dimension(:, :) :: var1, var2
    real(dp), intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    real(dp) :: tol

    n = size(var1, 1)
    m = size(var1, 2)

    if ((size(var2, 1) .ne. n) .and. (size(var2, 2) .ne. m)) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(n)//' x '//to_s(m), &
          & to_s(size(var2, 1))//' x '//to_s(size(var2, 1)), &
          & '2d arrays have different sizes, '//message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    tol = eps_dp
    if (present(delta)) tol = delta

    do j = 1, m
      do i = 1, n
        if (abs(real(var1(i, j) - var2(i, j), kind=dp)) > tol .or. &
          abs(dimag(var1(i, j) - var2(i, j))) > tol) then
          if (.not. present(status)) then
            call failed_assert_action( &
              & to_s(var1(i, j)), &
              & to_s(var2(i, j)), '2d array has difference, '//message, if_is=.true.)
          else
            status = .false.
          endif
          return
        endif
      enddo
    enddo
    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_eq_2d_complex_double_

  !------ 0d_logical ------
  subroutine assert_not_eq_logical_(var1, var2, message, status)
    logical, intent(in) :: var1, var2
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    call assert_equal(var1, var2, status=is_equal)

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1), &
          & to_s(var2), message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_logical_

  !------ 1d_logical ------
  subroutine assert_not_eq_1d_logical_(var1, var2, message, status)
    logical, intent(in), dimension(:) :: var1, var2
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    call assert_equal(var1, var2, status=is_equal)

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(1)), &
          & to_s(var2(1)), '1d array has no difference, '//message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_1d_logical_

  !------ 2d_logical ------
  subroutine assert_not_eq_2d_logical_(var1, var2, message, status)
    logical, intent(in), dimension(:, :) :: var1, var2
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    call assert_equal(var1, var2, status=is_equal)

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(1, 1)), &
          & to_s(var2(1, 1)), '2d array has no difference, '//message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_2d_logical_

  !------ 0d_string ------
  subroutine assert_not_eq_string_(var1, var2, message, status)
    character(len=*), intent(in) :: var1, var2
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    call assert_equal(var1, var2, status=is_equal)

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1), &
          & to_s(var2), message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif

  end subroutine assert_not_eq_string_

  !------ 1d_string ------
  subroutine assert_not_eq_1d_string_(var1, var2, message, status)
    character(len=*), intent(in), dimension(:) :: var1, var2
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    call assert_equal(var1, var2, status=is_equal)

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(1)), &
          & to_s(var2(1)), '1d array has no difference, '//message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_1d_string_

  !------ 2d_string ------
  subroutine assert_not_eq_2d_string_(var1, var2, message, status)
    character(len=*), intent(in), dimension(:, :) :: var1, var2
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    call assert_equal(var1, var2, status=is_equal)

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(1, 1)), &
          & to_s(var2(1, 1)), '2d array has no difference, '//message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_2d_string_

  !------ 0d_int ------
  subroutine assert_not_eq_int_(var1, var2, message, status)
    integer, intent(in) :: var1, var2
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    call assert_equal(var1, var2, status=is_equal)

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1), &
          & to_s(var2), message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_int_

  !------ 1d_int ------
  subroutine assert_not_eq_1d_int_(var1, var2, message, status)
    integer, intent(in), dimension(:) :: var1, var2
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    call assert_equal(var1, var2, status=is_equal)

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(1)), &
          & to_s(var2(1)), '1d array has no difference, '//message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_1d_int_

  !------ 2d_int ------
  subroutine assert_not_eq_2d_int_(var1, var2, message, status)
    integer, intent(in), dimension(:, :) :: var1, var2
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    call assert_equal(var1, var2, status=is_equal)

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(1, 1)), &
          & to_s(var2(1, 1)), '2d array has no difference, '//message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_2d_int_

  !------ 0d_real ------
  subroutine assert_not_eq_real_(var1, var2, delta, message, status)
    real, intent(in) :: var1, var2
    real, intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    if (present(delta)) then
      call assert_equal(var1, var2, delta, status=is_equal)
    else
      call assert_equal(var1, var2, status=is_equal)
    endif

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1), &
          & to_s(var2), message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_real_

  !------ 1d_real ------
  subroutine assert_not_eq_1d_real_(var1, var2, delta, message, status)
    real, intent(in), dimension(:) :: var1, var2
    real, intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    if (present(delta)) then
      call assert_equal(var1, var2, delta, status=is_equal)
    else
      call assert_equal(var1, var2, status=is_equal)
    endif

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(1)), &
          & to_s(var2(1)), '1d array has no difference, '//message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_1d_real_

  !------ 2d_real ------
  subroutine assert_not_eq_2d_real_(var1, var2, delta, message, status)
    real, intent(in), dimension(:, :) :: var1, var2
    real, intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    if (present(delta)) then
      call assert_equal(var1, var2, delta, status=is_equal)
    else
      call assert_equal(var1, var2, status=is_equal)
    endif

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(1, 1)), &
          & to_s(var2(1, 1)), '2d array has no difference, '//message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_2d_real_

  !------ 0d_double ------
  subroutine assert_not_eq_double_(var1, var2, delta, message, status)
    real(dp), intent(in) :: var1, var2
    real(dp), intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    if (present(delta)) then
      call assert_equal(var1, var2, delta, status=is_equal)
    else
      call assert_equal(var1, var2, status=is_equal)
    endif

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1), &
          & to_s(var2), message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_double_

  !------ 1d_double ------
  subroutine assert_not_eq_1d_double_(var1, var2, delta, message, status)
    real(dp), intent(in), dimension(:) :: var1, var2
    real(dp), intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    if (present(delta)) then
      call assert_equal(var1, var2, delta, status=is_equal)
    else
      call assert_equal(var1, var2, status=is_equal)
    endif

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(1)), &
          & to_s(var2(1)), '1d array has no difference, '//message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_1d_double_

  !------ 2d_double ------
  subroutine assert_not_eq_2d_double_(var1, var2, delta, message, status)
    real(dp), intent(in), dimension(:, :) :: var1, var2
    real(dp), intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    if (present(delta)) then
      call assert_equal(var1, var2, delta, status=is_equal)
    else
      call assert_equal(var1, var2, status=is_equal)
    endif

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(1, 1)), &
          & to_s(var2(1, 1)), '2d array has no difference, '//message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_2d_double_

  !------ 0d_complex_real_ ------
  subroutine assert_not_eq_complex_real_(var1, var2, delta, message, status)
    complex, intent(in) :: var1, var2
    real, intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    if (present(delta)) then
      call assert_equal(var1, var2, delta, status=is_equal)
    else
      call assert_equal(var1, var2, status=is_equal)
    endif

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1), &
          & to_s(var2), message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_complex_real_

  !------ 1d_complex_real_------
  subroutine assert_not_eq_1d_complex_real_(var1, var2, delta, message, status)
    complex, intent(in), dimension(:) :: var1, var2
    real, intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    if (present(delta)) then
      call assert_equal(var1, var2, delta, status=is_equal)
    else
      call assert_equal(var1, var2, status=is_equal)
    endif

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(1)), &
          & to_s(var2(1)), '1d array has no difference, '//message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_1d_complex_real_

  !------ 2d_complex_real_------
  subroutine assert_not_eq_2d_complex_real_(var1, var2, delta, message, status)
    complex, intent(in), dimension(:, :) :: var1, var2
    real, intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    if (present(delta)) then
      call assert_equal(var1, var2, status=is_equal)
    else
      call assert_equal(var1, var2, status=is_equal)
    endif

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(1, 1)), &
          & to_s(var2(1, 1)), '2d array has no difference, '//message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_2d_complex_real_

  !------ 0d_complex_double_ ------
  subroutine assert_not_eq_complex_double_(var1, var2, delta, message, status)
    complex(dp), intent(in) :: var1, var2
    real(dp), intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    if (present(delta)) then
      call assert_equal(var1, var2, delta, status=is_equal)
    else
      call assert_equal(var1, var2, status=is_equal)
    endif

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1), &
          & to_s(var2), message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_complex_double_

  !------ 1d_complex_double_------
  subroutine assert_not_eq_1d_complex_double_(var1, var2, delta, message, status)
    complex(dp), intent(in), dimension(:) :: var1, var2
    real(dp), intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    if (present(delta)) then
      call assert_equal(var1, var2, delta, status=is_equal)
    else
      call assert_equal(var1, var2, status=is_equal)
    endif

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(1)), &
          & to_s(var2(1)), '1d array has no difference, '//message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_1d_complex_double_

  !------ 2d_complex_double_------
  subroutine assert_not_eq_2d_complex_double_(var1, var2, delta, message, status)
    complex(dp), intent(in), dimension(:, :) :: var1, var2
    real(dp), intent(in), optional :: delta
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    if (present(delta)) then
      call assert_equal(var1, var2, delta, status=is_equal)
    else
      call assert_equal(var1, var2, status=is_equal)
    endif

    if (is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & to_s(var1(1, 1)), &
          & to_s(var2(1, 1)), '2d array has no difference, '//message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    if (.not. present(status)) then
      call add_success
    else
      status = .true.
    endif
  end subroutine assert_not_eq_2d_complex_double_

  subroutine assert_identical(filename1, filename2, message, status)
    !! category: testcase subroutine
    !! Compare two files and return true if identical
    character(len=*), intent(in) :: filename1, filename2
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    integer :: size1, size2, iostatVal
    character(:), allocatable :: contents1, contents2
    logical :: file_exists, is_equal

    ! Check file existence filename1
    inquire(file=filename1, exist=file_exists)
    if (.not. file_exists) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & filename1, 'none', &
          & 'File does not exist, '// message, if_is=.false.)
      else
        status = .false.
      endif
      return
    endif

    ! Check file existence filename2
    inquire(file=filename2, exist=file_exists)
    if (.not. file_exists) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & filename2, 'none', &
          & 'File does not exist, '// message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif

    open(unit=10, file=filename1, action="read", &
      & form="unformatted", access="stream", iostat=iostatVal)
    if (iostatVal .ne. 0) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & filename1, 'none', &
          'File appears empty or does not exist, '// message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif
    inquire(unit=10, size=size1)

    open(unit=11, file=filename2, action="read", &
      & form="unformatted", access="stream", iostat=iostatVal)
    if (iostatVal .ne. 0) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & filename2, 'none', &
          'File appears empty or does not exist, '// message, if_is=.true.)
      else
        status = .false.
      endif
      return
    endif
    inquire(unit=11, size=size2)

    ! Check sizes
    call assert_equal(size1, size2, status=is_equal)
    if (.not. is_equal) then
      if (.not. present(status)) then
        call failed_assert_action( &
          & filename1, filename2, &
          & 'Files do not match, '// message, if_is=.true.)
      else
        status= .false.
      endif
      close(10)
      close(11)
      return
    else
      allocate(character(size1) :: contents1)
      read(10) contents1
      close(10)

      allocate(character(size2) :: contents2)
      read(11) contents2
      close(11)
    endif

    ! Check contents
    call assert_equal(contents1, contents2, status=is_equal)

    if (is_equal) then
      if (.not. present(status)) then
        call add_success()
      else
        status =.true.
      endif
    else
      if (.not. present(status)) then
        call failed_assert_action( &
          & filename1, filename2, &
          & 'Files do not match, ' // message, if_is=.true.)
      else
        status = .false.
      endif
    endif
  end subroutine assert_identical

  subroutine assert_not_identical(filename1, filename2, message, status)
    !! category: testcase subroutine
    !! Compare two files and return true if not identical
    character(len=*), intent(in) :: filename1, filename2
    character(len=*), intent(in), optional :: message
    logical, intent(out), optional :: status
    logical :: is_equal

    call assert_identical(filename1, filename2, status=is_equal)

    if (is_equal) then
      if (.not. present(status)) then
        call add_success()
      else
        status =.true.
      endif
    else
      if (.not. present(status)) then
        call failed_assert_action( &
          & filename1, filename2, &
          & 'Files do match, ' // message, if_is=.false.)
      else
        status = .false.
      endif
    endif
  end subroutine assert_not_identical

  !====== end of generated code ======

  function to_s_int_(value)
    !! category: fruit_util
    !! Convert integer to string
    character(len=500):: to_s_int_
    integer, intent(in) :: value
    character(len=500) :: result
    write (result, *) value
    to_s_int_ = adjustl(trim(result))
  end function to_s_int_

    function to_s_real_(value)
    !! Convert real to string
    character(len=500):: to_s_real_
    real, intent(in) :: value
    character(len=500) :: result
    write (result, *) value
    to_s_real_ = adjustl(trim(result))
  end function to_s_real_

  function to_s_double_(value)
    !! Convert double to string
    character(len=500):: to_s_double_
    real(dp), intent(in) :: value
    character(len=500) :: result
    write (result, *) value
    to_s_double_ = adjustl(trim(result))
  end function to_s_double_

  function to_s_complex_(value)
    !! Convert complex to string
    character(len=500):: to_s_complex_
    complex, intent(in) :: value
    character(len=500) :: result
    write (result, *) value
    to_s_complex_ = adjustl(trim(result))
  end function to_s_complex_

  function to_s_double_complex_(value)
    !! Convert complex double to string
    character(len=500):: to_s_double_complex_
    complex(dp), intent(in) :: value
    character(len=500) :: result
    write (result, *) value
    to_s_double_complex_ = adjustl(trim(result))
  end function to_s_double_complex_

  function to_s_logical_(value)
    !! Convert logical to string
    character(len=500):: to_s_logical_
    logical, intent(in) :: value
    character(len=500) :: result
    write (result, *) value
    to_s_logical_ = adjustl(trim(result))
  end function to_s_logical_

  function to_s_string_(value)
    !! Convert string to string
    character(len=500):: to_s_string_
    character(len=*), intent(in) :: value
    to_s_string_ = value
  end function to_s_string_

  function findfalse_1d_(logical_array)
    !! Returns first occurence of .false. in logical_array
    logical, intent(in), dimension(:) :: logical_array
    integer, dimension(1) :: findfalse_1d_
    integer :: i
    do i = 1, size(logical_array, 1)
      if (logical_array(i) .eqv. .false.) then
        findfalse_1d_ = (/i/)
        return
      endif
    enddo
    findfalse_1d_ = (/0/)
  end function findfalse_1d_

  function findfalse_2d_(logical_array)
    !! Returns first occurence of .false. in logical_array
    logical, intent(in), dimension(:, :) :: logical_array
    integer, dimension(2) :: findfalse_2d_
    integer :: i, j
    do j = 1, size(logical_array, 2)
      do i = 1, size(logical_array, 1)
        if (logical_array(i, j) .eqv. .false.) then
          findfalse_2d_= (/i, j/)
          return
        endif
      enddo
    enddo
    findfalse_2d_ = (/0, 0/)
  end function findfalse_2d_
end module naturalfruit