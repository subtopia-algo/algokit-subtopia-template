<div align="center">
<a href="https://github.com/subtopia-algo/algokit-subtopia-template"><img src="https://bafybeidbdaq576qdekealqyfpgqzfdxobc5zifrko3b4afib3ezr3g3gyy.ipfs.nftstorage.link/" width=60%></a>
</div>

<p align="center">
    <a href="https://www.npmjs.com/package/subtopia-js-sdk"><img src="https://badge.fury.io/js/subtopia-js-sdk.svg" alt="npm version"></a>
    <a href="https://subtopia.io"><img src="https://img.shields.io/badge/platform-link-cyan.svg" /></a>
    <a href="https://github.com/algorandfoundation/algokit-cli"><img src="https://img.shields.io/badge/Powered by-AlgoKit-black.svg" /></a>
</p>

---

This template is a starter template for building an Algorand based dApp on React with [`subtopia-js-sdk`](https://github.com/subtopia-algo/subtopia-js) integration. The template is based on the official [`algokit-react-template`](https://github.com/algorandfoundation/algokit-react-frontend-template).

## Features

The template offers two presets, the recommended preset includes all of the above, a custom preset allows you to select which features you want to include in your project.

The full list of features includes the following:

- Subtopia SDK integration for interacting with the Subtopia protocol. Includes a sample TestNet based subscription integrated.
- React web app with [Tailwind CSS](https://tailwindcss.com/) and [TypeScript](https://www.typescriptlang.org/)
- Styled framework agnostic CSS components using [DaisyUI](https://daisyui.com/).
- Starter jest unit tests for typescript functions. Can be disabled if not needed.
- Starter [playwright](https://playwright.dev/) tests for end to end testing. Can be disabled if not needed.
- Integration with [use-wallet](https://github.com/txnlab/use-wallet) for connecting to Algorand wallets such as Pera, Defly and Exodus.
- Example of performing a transaction.
- Dotenv support for environment variables, as well as a local only KMD provider that can be used for connecting the frontend component to an `algokit localnet` instance (docker required).
- CI/CD pipeline using GitHub Actions (Vercel or Netlify for hosting)

# Getting started

Once the template is instantiated you can follow the [README.md](template_content/README.md.jinja) file to see instructions for how to use the template.
