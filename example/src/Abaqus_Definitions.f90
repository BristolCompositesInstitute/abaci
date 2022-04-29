!DIR$ FREEFORM
module Abaqus_Definitions
  ! This module exports various Abaqus Fortran definitions including 
  ! a kind parameter "abaqus_real_kind" that defines the real kind (precision)
  ! currently in use by Abaqus. This allows explict typing in Fortran user subroutines.
  !
  ! USAGE:
  !  1) Include this file at the beginning of your top-level user subroutine file:
  !      include 'Abaqus_Definitions.f'
  !
  !  2) Import the module in your modules/subroutines with the following syntax:
  !      use Abaqus_Definitions, only: wp=>abaqus_real_kind
  !
  !  3) Define real parameters from Abaqus with the following syntax:
  !      real(wp) :: hsvNew(:,:)
  !
  ! Laurence Kedward March 2022

!DIR$ NOFREEFORM
!DIR$ FIXEDFORMLINESIZE:132
      include "aba_param.inc"
!DIR$ FREEFORM

  private

  ! Detect and export the Abaqus real kind precision
  parameter(a = 0)
  integer, parameter, public :: abaqus_real_kind = kind(a)
  
  ! vexternaldb i_Array contents enumerator
  integer, parameter, public :: i_int_nTotalNodes     = 1, &
                                i_int_nTotalElements  = 2, &
                                i_int_kStep           = 3, &
                                i_int_kInc            = 4, &
                                i_int_iStatus         = 5


  ! vexternaldb lOp enumerator
  integer, parameter, public :: j_int_StartAnalysis    = 0, &
                                j_int_StartStep        = 1, &
                                j_int_SetupIncrement   = 2, &
                                j_int_StartIncrement   = 3, &
                                j_int_EndIncrement     = 4, &
                                j_int_EndStep          = 5, &
                                j_int_EndAnalysis      = 6 

  ! vexternaldb i_Array(i_int_iStatus) enumerator
  integer, parameter, public :: j_int_Continue          = 0, &
                                j_int_TerminateStep     = 1, &
                                j_int_TerminateAnalysis = 2

  ! vexternaldb r_Array contents enumerator
  integer, parameter, public :: i_flt_TotalTime   = 1, &
                                i_flt_StepTime    = 2, &
                                i_flt_dTime       = 3

end module Abaqus_Definitions
!DIR$ NOFREEFORM
!DIR$ FIXEDFORMLINESIZE:132
