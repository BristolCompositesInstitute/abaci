#include 'Abaqus_Definitions.f90'
#include 'Elastic_mod.f90'
!DIR$ FREEFORM

!> Example UMAT reproducing linear elastic behaviour
subroutine umat(stress,statev,ddsdde,sse,spd,scd, &
  rpl,ddsddt,drplde,drpldt, &
  stran,dstran,time,dtime,temp,dtemp,predef,dpred,cmname, &
  ndi,nshr,ntens,nstatv,props_array,nprops,coords,drot,pnewdt, &
  celent,dfgrd0,dfgrd1,noel,npt,layer,kspt,jstep,kinc)

  use Abaqus_Definitions, only: wp=>abaqus_real_kind
  use Elastic_mod
  implicit none

  real(dp), intent(inout) :: stress(ntens), statev(nstatv), ddsdde(ntens,ntens)
  real(dp), intent(inout) :: sse, spd, scd, rpl, ddsddt(ntens), drplde(ntens)
  real(dp), intent(inout) :: drpldt
  real(dp), intent(in) :: stran(ntens), dstran(ntens), time(2), dtime, temp
  real(dp), intent(in) :: dtemp, predef(1), dpred(1)
  character(len=80), intent(in) :: cmname
  integer, intent(in) :: ndi, nshr, ntens, nstatv, nprops
  real(dp), intent(in) :: props_array(nprops), coords(3), drot(3, 3), pnewdt
  real(dp), intent(in) :: celent, dfgrd0(3,3), dfgrd1(3,3)
  integer, intent(in) :: noel, npt, layer, kspt, jstep(4), kinc

  
  if (cmname(1:12) == 'UMAT_ELASTIC') then

    call umat_elastic(ddsdde, stress, props_array, dstran, ndi, nshr)

  ! elseif (cmname == 'UMAT_OTHER') then

    ! call some other material subroutine

  else

    write(*,*) ' (!) UMAT ERROR: Unrecognized user material name "'//trim(cmname)//'"'
    call xit()

  end if
  
end subroutine umat
