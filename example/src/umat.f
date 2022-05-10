#include 'Abaqus_Definitions.f90'
!DIR$ FREEFORM

!> Example UMAT reproducing linear elastic behaviour
subroutine umat(stress,statev,ddsdde,sse,spd,scd, &
  rpl,ddsddt,drplde,drpldt, &
  stran,dstran,time,dtime,temp,dtemp,predef,dpred,cmname, &
  ndi,nshr,ntens,nstatv,props,nprops,coords,drot,pnewdt, &
  celent,dfgrd0,dfgrd1,noel,npt,layer,kspt,jstep,kinc)

  use Abaqus_Definitions, only: wp=>abaqus_real_kind
  implicit none

  !> Stress tensor
  real(wp), intent(inout) :: stress(ntens)

  !> Solution-dependent state variables
  real(wp), intent(inout) :: statev(nstatv)

  !> Jacobian of the constitutive model
  real(wp), intent(inout) :: ddsdde(ntens,ntens)

  !> Specific elastic strain energy, plastic diss & creep diss
  real(wp), intent(inout) :: sse, spd, scd

  !> Parameters for fully-coupled thermal-stress analysis
  real(wp), intent(inout) :: rpl            !> Volumetric heat generation per unit time
  real(wp), intent(inout) :: ddsddt(ntens)  !> Variation of stress increments wrt temperature
  real(wp), intent(inout) :: drplde(ntens)  !> Variable of rpl wrt strain increments
  real(wp), intent(inout) :: drpldt         !> Variable of rpl wrt temperature

  !> Total strains at beginning of increment
  real(wp), intent(in) :: stran(ntens)

  !> Strain increments
  real(wp), intent(in) :: dstran(ntens)

  !> Value of step time (1) and total time (2) at beginning of current incremental
  real(wp), intent(in) :: time(2)

  !> Time increment
  real(wp), intent(in) :: dtime

  !> Temperature at start of the increment
  real(wp), intent(in) :: temp

  !> Increment of temperature
  real(wp), intent(in) :: dtemp

  !> Interpolated values of predefined field variables
  real(wp), intent(in) :: predef(1)

  !> Increments of predefined field variables
  real(wp), intent(in) :: dpred(1)

  !> User-defined material name
  character(len=80), intent(in) :: cmname

  integer, intent(in) :: ndi         !! number of stress components at this point
  integer, intent(in) :: nshr        !! number of engineering shear stress components at this point
  integer, intent(in) :: ntens       !! size of stress of strain component array (ndi + nshr)
  integer, intent(in) :: nstatv      !! number of solution-dependent state variables
  integer, intent(in) :: nprops      !! number of user-specified material constants

  !> User-specified material constants
  real(wp), intent(in) :: props(nprops)

  !> Coordinates of this point
  real(wp), intent(in) :: coords(3)

  !> Rotation increment matrix
  real(wp), intent(in) :: drot(3, 3)

  !> Ratio of suggested new time increment to the time increment being used
  real(wp), intent(inout) :: pnewdt

  !> Characteristic element length
  real(wp), intent(in) :: celent

  !> Defromation gradient at beginning of increment
  real(wp), intent(in) :: dfgrd0(3,3)

  !> Defromation gradient at end of increment
  real(wp), intent(in) :: dfgrd1(3,3)

  integer, intent(in) :: noel         !! element number
  integer, intent(in) :: npt          !! integration point number
  integer, intent(in) :: layer        !! layer number
  integer, intent(in) :: kspt         !! section point number
  integer, intent(in) :: jstep(4)     !! Step number of information
  integer, intent(in) :: kinc         !! Increment number

  ! Local variables
  real(wp) :: e,xnu
  integer i,j

  ddsdde = 0.d0

  e = props(1)
  xnu = props(2)

  if (ndi==3 .and. nshr==1) then    ! plane strain or axisymmetry
    ddsdde(1,1) = 1.d0-xnu
    ddsdde(1,2) = xnu
    ddsdde(1,3) = xnu
    ddsdde(2,1) = xnu
    ddsdde(2,2) = 1.d0-xnu
    ddsdde(2,3) = xnu
    ddsdde(3,1) = xnu
    ddsdde(3,2) = xnu
    ddsdde(3,3) = 1.d0-xnu
    ddsdde(4,4) = 0.5d0*(1.d0-2.d0*xnu)
    ddsdde = ddsdde*e/( (1.d0+xnu)*(1.d0-2.d0*xnu) )
  else if (ndi==2 .and. nshr==1) then   ! plane stress
    ddsdde(1,1) = 1.d0
    ddsdde(1,2) = xnu
    ddsdde(2,1) = xnu
    ddsdde(2,2) = 1.d0
    ddsdde(3,3) = 0.5d0*(1.d0-xnu)
    ddsdde = ddsdde*e/( (1.d0+xnu*xnu) )
  else ! 3d
    ddsdde(1,1) = 1.d0-xnu
    ddsdde(1,2) = xnu
    ddsdde(1,3) = xnu
    ddsdde(2,1) = xnu
    ddsdde(2,2) = 1.d0-xnu
    ddsdde(2,3) = xnu
    ddsdde(3,1) = xnu
    ddsdde(3,2) = xnu
    ddsdde(3,3) = 1.d0-xnu
    ddsdde(4,4) = 0.5d0*(1.d0-2.d0*xnu)
    ddsdde(5,5) = ddsdde(4,4)
    ddsdde(6,6) = ddsdde(4,4)
    ddsdde = ddsdde*e/( (1.d0+xnu)*(1.d0-2.d0*xnu) )
  end if

  do i = 1,ntens
    do j = 1,ntens
      stress(i) = stress(i) + ddsdde(i,j)*dstran(j)
    end do
  end do
  
end subroutine umat
