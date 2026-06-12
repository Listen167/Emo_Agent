import type { Directive } from 'vue'

const observerMap = new WeakMap<Element, IntersectionObserver>()

export const developDirective: Directive<HTMLElement, number | undefined> = {
  mounted(el, binding) {
    const delay = Number(binding.value || 0)
    el.classList.add('develop-reveal')
    if (delay > 0) {
      el.style.setProperty('--develop-delay', `${delay}ms`)
    }

    const observer = new IntersectionObserver(
      entries => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          entry.target.classList.add('develop-reveal-visible')
          observer.unobserve(entry.target)
        }
      },
      {
        rootMargin: '0px 0px -8% 0px',
        threshold: 0.12,
      }
    )

    observer.observe(el)
    observerMap.set(el, observer)
  },

  unmounted(el) {
    observerMap.get(el)?.disconnect()
    observerMap.delete(el)
  },
}
