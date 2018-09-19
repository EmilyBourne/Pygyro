module mod_pygyro_initialisation_initialiser_func

use mod_initialiser_funcs, only: fEq
use mod_initialiser_funcs, only: perturbation
implicit none



contains

! ........................................
subroutine init_f(r, theta, z, vPar, m, n, eps, CN0, kN0, deltaRN0, rp, &
      CTi, kTi, deltaRTi, deltaR, R0, result_1786)

  implicit none
  real(kind=8), intent(out)  :: result_1786
  real(kind=8), intent(in)  :: r
  real(kind=8), intent(in)  :: theta
  real(kind=8), intent(in)  :: z
  real(kind=8), intent(in)  :: vPar
  integer(kind=4), intent(in)  :: m
  integer(kind=4), intent(in)  :: n
  real(kind=8), intent(in)  :: eps
  real(kind=8), intent(in)  :: CN0
  real(kind=8), intent(in)  :: kN0
  real(kind=8), intent(in)  :: deltaRN0
  real(kind=8), intent(in)  :: rp
  real(kind=8), intent(in)  :: CTi
  real(kind=8), intent(in)  :: kTi
  real(kind=8), intent(in)  :: deltaRTi
  real(kind=8), intent(in)  :: deltaR
  real(kind=8), intent(in)  :: R0

  result_1786 = (eps*perturbation(r, theta, z, m, n, rp, deltaR, R0) + 1 &
      )*fEq(r, vPar, CN0, kN0, deltaRN0, rp, CTi, kTi, deltaRTi)
  return


end subroutine
! ........................................

! ........................................
subroutine init_f_flux(n0_surface, n1_surface, surface, r, n0_theta, &
      theta, n0_zVec, zVec, vPar, m, n, eps, CN0, kN0, deltaRN0, rp, &
      CTi, kTi, deltaRTi, deltaR, R0)

  implicit none
  integer(kind=4), intent(in)  :: n0_surface
  integer(kind=4), intent(in)  :: n1_surface
  real(kind=8), intent(inout)  :: surface (0:n0_surface - 1,0:n1_surface &
      - 1)
  real(kind=8), intent(in)  :: r
  integer(kind=4), intent(in)  :: n0_theta
  real(kind=8), intent(in)  :: theta (0:n0_theta - 1)
  integer(kind=4), intent(in)  :: n0_zVec
  real(kind=8), intent(in)  :: zVec (0:n0_zVec - 1)
  real(kind=8), intent(in)  :: vPar
  integer(kind=4), intent(in)  :: m
  integer(kind=4), intent(in)  :: n
  real(kind=8), intent(in)  :: eps
  real(kind=8), intent(in)  :: CN0
  real(kind=8), intent(in)  :: kN0
  real(kind=8), intent(in)  :: deltaRN0
  real(kind=8), intent(in)  :: rp
  real(kind=8), intent(in)  :: CTi
  real(kind=8), intent(in)  :: kTi
  real(kind=8), intent(in)  :: deltaRTi
  real(kind=8), intent(in)  :: deltaR
  real(kind=8), intent(in)  :: R0
  real(kind=8) :: q
  integer(kind=4) :: j
  real(kind=8) :: z
  integer(kind=4) :: i

  do i = 0, n0_theta - 1, 1
    q = theta(i)
    do j = 0, n0_zVec - 1, 1
      z = zVec(j)
      surface(j, i) = (eps*perturbation(r, q, z, m, n, rp, deltaR, R0) + &
      1)*fEq(r, vPar, CN0, kN0, deltaRN0, rp, CTi, kTi, deltaRTi)


    end do

  end do

end subroutine
! ........................................

! ........................................
subroutine init_f_pol(n0_surface, n1_surface, surface, n0_rVec, rVec, &
      n0_theta, theta, z, vPar, m, n, eps, CN0, kN0, deltaRN0, rp, CTi, &
      kTi, deltaRTi, deltaR, R0)

  implicit none
  integer(kind=4), intent(in)  :: n0_surface
  integer(kind=4), intent(in)  :: n1_surface
  real(kind=8), intent(inout)  :: surface (0:n0_surface - 1,0:n1_surface &
      - 1)
  integer(kind=4), intent(in)  :: n0_rVec
  real(kind=8), intent(in)  :: rVec (0:n0_rVec - 1)
  integer(kind=4), intent(in)  :: n0_theta
  real(kind=8), intent(in)  :: theta (0:n0_theta - 1)
  real(kind=8), intent(in)  :: z
  real(kind=8), intent(in)  :: vPar
  integer(kind=4), intent(in)  :: m
  integer(kind=4), intent(in)  :: n
  real(kind=8), intent(in)  :: eps
  real(kind=8), intent(in)  :: CN0
  real(kind=8), intent(in)  :: kN0
  real(kind=8), intent(in)  :: deltaRN0
  real(kind=8), intent(in)  :: rp
  real(kind=8), intent(in)  :: CTi
  real(kind=8), intent(in)  :: kTi
  real(kind=8), intent(in)  :: deltaRTi
  real(kind=8), intent(in)  :: deltaR
  real(kind=8), intent(in)  :: R0
  real(kind=8) :: q
  real(kind=8) :: r
  integer(kind=4) :: j
  integer(kind=4) :: i

  do i = 0, n0_theta - 1, 1
    q = theta(i)
    do j = 0, n0_rVec - 1, 1
      r = rVec(j)
      surface(j, i) = (eps*perturbation(r, q, z, m, n, rp, deltaR, R0) + &
      1)*fEq(r, vPar, CN0, kN0, deltaRN0, rp, CTi, kTi, deltaRTi)


    end do

  end do

end subroutine
! ........................................

! ........................................
subroutine init_f_vpar(n0_surface, n1_surface, surface, r, n0_theta, &
      theta, z, n0_vPar, vPar, m, n, eps, CN0, kN0, deltaRN0, rp, CTi, &
      kTi, deltaRTi, deltaR, R0)

  implicit none
  integer(kind=4), intent(in)  :: n0_surface
  integer(kind=4), intent(in)  :: n1_surface
  real(kind=8), intent(inout)  :: surface (0:n0_surface - 1,0:n1_surface &
      - 1)
  real(kind=8), intent(in)  :: r
  integer(kind=4), intent(in)  :: n0_theta
  real(kind=8), intent(in)  :: theta (0:n0_theta - 1)
  real(kind=8), intent(in)  :: z
  integer(kind=4), intent(in)  :: n0_vPar
  real(kind=8), intent(in)  :: vPar (0:n0_vPar - 1)
  integer(kind=4), intent(in)  :: m
  integer(kind=4), intent(in)  :: n
  real(kind=8), intent(in)  :: eps
  real(kind=8), intent(in)  :: CN0
  real(kind=8), intent(in)  :: kN0
  real(kind=8), intent(in)  :: deltaRN0
  real(kind=8), intent(in)  :: rp
  real(kind=8), intent(in)  :: CTi
  real(kind=8), intent(in)  :: kTi
  real(kind=8), intent(in)  :: deltaRTi
  real(kind=8), intent(in)  :: deltaR
  real(kind=8), intent(in)  :: R0
  real(kind=8) :: v
  real(kind=8) :: q
  integer(kind=4) :: i
  integer(kind=4) :: j

  do i = 0, n0_theta - 1, 1
    q = theta(i)
    do j = 0, n0_vPar - 1, 1
      v = vPar(j)
      surface(j, i) = (eps*perturbation(r, q, z, m, n, rp, deltaR, R0) + &
      1)*fEq(r, v, CN0, kN0, deltaRN0, rp, CTi, kTi, deltaRTi)


    end do

  end do

end subroutine
! ........................................

end module