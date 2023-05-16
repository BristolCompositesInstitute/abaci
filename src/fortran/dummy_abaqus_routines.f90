integer function get_thread_id()
  get_thread_id = 0
end function get_thread_id

integer function getnumthreads()
  getnumthreads = 1
end function getnumthreads

integer function getcommunicator()
  getcommunicator = 0
end function getcommunicator

subroutine getrank(n)
  integer, intent(out) :: n
  n = 0
end subroutine getrank

subroutine vgetrank(n)
  integer, intent(out) :: n
  n = 0
end subroutine vgetrank

subroutine getnumcpus(n)
  integer, intent(out) :: n
  n = 1
end subroutine getnumcpus

subroutine vgetnumcpus(n)
  integer, intent(out) :: n
  n = 1
end subroutine vgetnumcpus

